#!/usr/bin/env bash
# Detect the current repository, ensure its own Project, and add missing configuration.
set -Eeuo pipefail
export GH_HOST=github.com

usage() {
  echo 'Usage: setup.sh [--apply]   (run inside the repository to configure)'
  echo 'Without --apply, show missing configuration without changing GitHub.'
}

stop() {
  echo "ERROR: $*" >&2
  exit 2
}

trap 'echo "ERROR: Step failed at line $LINENO. Changes may be partial; inspect GitHub before rerunning." >&2' ERR

check_requirements() {
  local tool
  local missing_tools=()

  for tool in git gh jq; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      missing_tools+=("$tool")
    fi
  done
  if ((${#missing_tools[@]} > 0)); then
    stop "Missing commands: ${missing_tools[*]}. Install them and rerun."
  fi

  if ! gh auth status --active --hostname github.com >/dev/null 2>&1; then
    stop 'GitHub authentication unavailable. Check gh auth status or run gh auth login.'
  fi
  local login
  login=$(gh api user --jq .login)
  [[ -n "$login" && "$login" != null ]] || stop 'GitHub returned no authenticated account.'
  echo "Authenticated as: $login"
}

detect_repository() {
  local remote
  git rev-parse --show-toplevel >/dev/null 2>&1 || stop 'Run this skill inside a Git repository.'
  remote=$(git remote get-url origin 2>/dev/null) || stop 'This repository has no origin remote.'

  case "$remote" in
    https://github.com/*) repo=${remote#https://github.com/} ;;
    git@github.com:*) repo=${remote#git@github.com:} ;;
    ssh://git@github.com/*) repo=${remote#ssh://git@github.com/} ;;
    *) stop 'The origin remote must identify a repository on github.com.' ;;
  esac
  repo=${repo%/}
  repo=${repo%.git}
  [[ "$repo" =~ ^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$ ]] || stop 'Cannot identify OWNER/REPO from origin.'

  # Ask GitHub for the canonical spelling, ID, and existing Project links.
  repository=$(gh repo view "$repo" --json nameWithOwner,id,projectsV2)
  repo=$(jq -er .nameWithOwner <<<"$repository")
  repo_id=$(jq -er .id <<<"$repository")
  owner=${repo%%/*}
  title=${repo#*/}
  echo "Repository: $repo"
}

select_project() {
  local projects count
  projects=$(jq -e '.projectsV2.Nodes // error("Cannot read repository Project links")' <<<"$repository")
  count=$(jq length <<<"$projects")

  case "$count" in
    0)
      echo "No linked Project. A new '$title' Project will be created and linked."
      if [[ "$apply" == false ]]; then
        project_id=''
        return
      fi
      project=$(gh project create --owner "$owner" --title "$title" --format json)
      number=$(jq -er .number <<<"$project")
      echo "Created Project: $(jq -r .url <<<"$project")"
      gh project link "$number" --owner "$owner" --repo "$repo"
      ;;
    1)
      number=$(jq -er '.[0].number' <<<"$projects")
      project=$(gh project view "$number" --owner "$owner" --format json)
      ;;
    *) stop 'This repository links to multiple Projects. Resolve the one-to-one conflict first.' ;;
  esac

  jq -e '.closed == false' <<<"$project" >/dev/null || stop 'The linked Project is closed; resolve that before setup.'
  project_id=$(jq -er .id <<<"$project")
  echo "Project: $(jq -r .url <<<"$project")"
}

check_project_owner() {
  # The reverse link must also be one-to-one: this Project belongs only to this repo.
  if ! jq -e --arg id "$repo_id" '
    (.repositories.nodes | length) == 1 and .repositories.nodes[0].id == $id
  ' <<<"$snapshot" >/dev/null; then
    stop 'The Project is not linked exclusively to this repository. Resolve the one-to-one conflict first.'
  fi
}

load_project() {
  local query result

  # Read IDs and existing option details so updates preserve them.
  read -r -d '' query <<'GRAPHQL' || true
query($id: ID!) {
  node(id: $id) {
    ... on ProjectV2 {
      fields(first: 100) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id
            name
            options { id name color description }
          }
        }
        pageInfo { hasNextPage }
      }
      repositories(first: 100) {
        nodes { id }
        pageInfo { hasNextPage }
      }
    }
  }
}
GRAPHQL
  result=$(gh api graphql -f query="$query" -f id="$project_id")
  snapshot=$(jq -e '.data.node // error("Cannot read Project configuration")' <<<"$result")
  if jq -e '.fields.pageInfo.hasNextPage or .repositories.pageInfo.hasNextPage' <<<"$snapshot" >/dev/null; then
    stop 'Project exceeds the supported page size; inspect it manually.'
  fi
  status_field=$(jq -e '
    [.fields.nodes[] | select(.name == "Status")]
    | if length == 1 then .[0] else error("Expected one Status field") end
  ' <<<"$snapshot")
}

save_status_options() {
  local query payload result

  # GitHub updates the complete option list; retain existing IDs and metadata.
  read -r -d '' query <<'GRAPHQL' || true
mutation($input: UpdateProjectV2FieldInput!) {
  updateProjectV2Field(input: $input) {
    projectV2Field { ... on ProjectV2SingleSelectField { id } }
  }
}
GRAPHQL
  payload=$(jq -n \
    --arg query "$query" \
    --arg field_id "$(jq -r .id <<<"$status_field")" \
    --argjson options "$options" \
    '{query: $query, variables: {input: {fieldId: $field_id, singleSelectOptions: $options}}}')
  result=$(gh api graphql --input - <<<"$payload")
  jq -e '.data.updateProjectV2Field != null and (.errors | length) == 0' <<<"$result" >/dev/null
}

ensure_statuses() {
  local expected name existing
  local missing=0
  options=$(jq '.options' <<<"$status_field")

  while IFS= read -r expected; do
    name=$(jq -r .name <<<"$expected")
    existing=$(jq -r --arg name "$name" '
      .[] | select((.name | ascii_downcase) == ($name | ascii_downcase)) | .name
    ' <<<"$options")

    if [[ "$existing" == "$name" ]]; then
      continue
    fi
    if [[ -n "$existing" ]]; then
      stop "Status '$existing' differs from '$name' only by case. Rename it explicitly first."
    fi

    echo "Missing status: $name"
    options=$(jq --argjson expected "$expected" '. + [$expected]' <<<"$options")
    missing=$((missing + 1))
  done < <(jq -c '.statuses[]' "$baseline_file")

  if ((missing == 0)); then
    echo 'Statuses: all required options exist.'
  elif [[ "$apply" == true ]]; then
    save_status_options
    echo "Added $missing missing status options."
  fi
}

ensure_labels() {
  local labels expected name color description
  local missing_labels=0
  labels=$(gh api "repos/$repo/labels?per_page=100" --paginate --slurp | jq 'add // []')

  while IFS= read -r expected; do
    name=$(jq -r .name <<<"$expected")
    if jq -e --arg name "$name" 'any(.[]; (.name | ascii_downcase) == ($name | ascii_downcase))' <<<"$labels" >/dev/null; then
      continue
    fi

    echo "Missing label: $name"
    missing_labels=$((missing_labels + 1))
    if [[ "$apply" == true ]]; then
      color=$(jq -r .color <<<"$expected")
      description=$(jq -r .description <<<"$expected")
      gh label create "$name" --repo "$repo" --color "$color" --description "$description"
    fi
  done < <(jq -c '.labels[]' "$baseline_file")

  if ((missing_labels == 0)); then
    echo 'Labels: all required labels exist.'
  fi
}

verify_configuration() {
  local labels
  load_project
  check_project_owner
  labels=$(gh api "repos/$repo/labels?per_page=100" --paginate --slurp | jq 'add // []')

  jq -e --argjson field "$status_field" '
    [.statuses[].name] - [$field.options[].name] | length == 0
  ' "$baseline_file" >/dev/null
  jq -e --argjson labels "$labels" '
    [.labels[].name | ascii_downcase] - [$labels[].name | ascii_downcase] | length == 0
  ' "$baseline_file" >/dev/null
  jq -e --arg id "$repo_id" 'any(.repositories.nodes[]; .id == $id)' <<<"$snapshot" >/dev/null
  # Verify that no second Project was linked to the repository during setup.
  repository=$(gh repo view "$repo" --json nameWithOwner,id,projectsV2)
  jq -e --arg id "$project_id" '
    (.projectsV2.Nodes | length) == 1 and .projectsV2.Nodes[0].id == $id
  ' <<<"$repository" >/dev/null
  echo 'Verified: required statuses, labels, and the one-to-one Project link are present.'
}

# 1. The current repository is the target. Only --apply permits writes.
apply=false
while (($#)); do
  case "$1" in
    --apply) apply=true ;;
    -h|--help) usage; exit 0 ;;
    *) stop "Unknown argument: $1" ;;
  esac
  shift
done

# 2. Check prerequisites and read the baseline before making any GitHub changes.
check_requirements
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
baseline_file="$script_dir/baseline.json"
jq -e '
  (.statuses | type == "array" and length > 0)
  and (.labels | type == "array" and length > 0)
  and all(.statuses[], .labels[]; (.name | type == "string" and length > 0))
' "$baseline_file" >/dev/null

# 3. Reuse the linked Project, or create and link one when none exists.
detect_repository
select_project
if [[ -n "$project_id" ]]; then
  load_project
  check_project_owner
else
  # Preview can show the required configuration before the Project exists.
  status_field='{"options": []}'
fi

# 4. Add only missing values. Existing values and IDs remain untouched.
ensure_statuses
ensure_labels

# 5. Verify saved state after applying; preview never writes.
if [[ "$apply" == true ]]; then
  verify_configuration
else
  echo 'Preview only. Nothing changed; add --apply to create missing configuration.'
fi

echo 'Manual checklist: disable built-in workflows; use Board layout with Status columns.'
echo 'Existing extra statuses and labels are preserved; review unused factory statuses manually.'
