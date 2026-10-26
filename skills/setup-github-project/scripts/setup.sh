#!/usr/bin/env bash
# Detect the current repository and add missing Project configuration.
set -Eeuo pipefail
export GH_HOST=github.com
trap 'echo "ERROR: Failed at line $LINENO; inspect GitHub before retrying. Changes may be partial." >&2' ERR

stop() {
  echo "ERROR: $*" >&2
  exit 2
}

apply=false
case "${1:-}" in
'') ;;
--apply) apply=true ;;
-h | --help)
  echo 'Usage: setup.sh [--apply] (run inside the repository; default is preview)'
  exit 0
  ;;
*) stop "Unknown argument: $1" ;;
esac
(($# <= 1)) || stop 'Usage: setup.sh [--apply]'

for tool in git gh jq; do
  command -v "$tool" >/dev/null || stop "Missing command: $tool"
done
gh auth status --active --hostname github.com >/dev/null 2>&1 || stop 'GitHub authentication unavailable.'
baseline_file="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/baseline.json"
jq -e '
  (.statuses | type == "array" and length > 0) and
  (.labels | type == "array" and length > 0) and
  all(.statuses[], .labels[]; (.name | type == "string" and length > 0))
' "$baseline_file" >/dev/null

git rev-parse --show-toplevel >/dev/null 2>&1 || stop 'Run inside a Git repository.'
remote=$(git remote get-url origin 2>/dev/null) || stop 'This repository has no origin remote.'
case "$remote" in
https://github.com/*) repo=${remote#https://github.com/} ;;
git@*:* | ssh://git@*/*)
  if [[ "$remote" =~ ^git@([^/:]+):(.+)$ ]]; then
    ssh_host=${BASH_REMATCH[1]}
    repo=${BASH_REMATCH[2]}
  elif [[ "$remote" =~ ^ssh://git@([^/:]+)(:[0-9]+)?/(.+)$ ]]; then
    ssh_host=${BASH_REMATCH[1]}
    repo=${BASH_REMATCH[3]}
  else
    stop 'Cannot identify the SSH host and OWNER/REPO from origin.'
  fi
  if [[ "$ssh_host" != github.com ]]; then
    command -v ssh >/dev/null || stop 'SSH alias resolution requires ssh.'
    ssh_host=$(ssh -G -- "$ssh_host" 2>/dev/null | awk '$1 == "hostname" {print $2}')
    [[ "${ssh_host,,}" == github.com ]] || stop 'The SSH alias must resolve to github.com.'
  fi
  ;;
*) stop 'The origin remote must identify a repository on github.com.' ;;
esac
repo=${repo%/}
repo=${repo%.git}
[[ "$repo" =~ ^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$ ]] || stop 'Cannot identify OWNER/REPO from origin.'
repository=$(gh repo view "$repo" --json nameWithOwner,id,projectsV2)
repo=$(jq -er .nameWithOwner <<<"$repository")
repo_id=$(jq -er .id <<<"$repository")
owner=${repo%%/*}
echo "Repository: $repo"

# Used before configuration and again to verify the saved result.
load_project() {
  local result
  # shellcheck disable=SC2016 # $id is a GraphQL variable.
  result=$(gh api graphql -f id="$project_id" -f query='
    query($id: ID!) {
      node(id: $id) { ... on ProjectV2 {
        fields(first: 100) {
          nodes { ... on ProjectV2SingleSelectField {
            id name options { id name color description }
          } }
          pageInfo { hasNextPage }
        }
        repositories(first: 100) {
          nodes { id }
          pageInfo { hasNextPage }
        }
      } }
    }')
  snapshot=$(jq -e '.data.node // error("Cannot read Project")' <<<"$result")
  if jq -e '.fields.pageInfo.hasNextPage or .repositories.pageInfo.hasNextPage' <<<"$snapshot" >/dev/null; then
    stop 'Project exceeds the supported page size; inspect it manually.'
  fi
  jq -e --arg id "$repo_id" '
    (.repositories.nodes | length) == 1 and .repositories.nodes[0].id == $id
  ' <<<"$snapshot" >/dev/null || stop 'The Project is not linked exclusively to this repository.'
  status_field=$(jq -e '
    [.fields.nodes[] | select(.name == "Status")]
    | if length == 1 then .[0] else error("Expected one Status field") end
  ' <<<"$snapshot")
}

project_id=''
projects=$(jq -e '.projectsV2.Nodes // error("Cannot read Project links")' <<<"$repository")
case "$(jq length <<<"$projects")" in
0)
  echo "No linked Project. A new '${repo#*/}' Project will be created and linked."
  if [[ "$apply" == true ]]; then
    project=$(gh project create --owner "$owner" --title "${repo#*/}" --format json)
    number=$(jq -er .number <<<"$project")
    echo "Created Project: $(jq -r .url <<<"$project")"
    gh project link "$number" --owner "$owner" --repo "$repo"
  fi
  ;;
1)
  number=$(jq -er '.[0].number' <<<"$projects")
  project=$(gh project view "$number" --owner "$owner" --format json)
  ;;
*) stop 'This repository links to multiple Projects. Resolve the one-to-one conflict first.' ;;
esac

status_field='{"options": []}'
if [[ -n "${project:-}" ]]; then
  jq -e '.closed == false' <<<"$project" >/dev/null || stop 'The linked Project is closed.'
  project_id=$(jq -er .id <<<"$project")
  echo "Project: $(jq -r .url <<<"$project")"
  load_project
fi

# GitHub replaces the entire option list: retain existing IDs and metadata.
options=$(jq .options <<<"$status_field")
missing=0
while IFS= read -r expected; do
  name=$(jq -r .name <<<"$expected")
  existing=$(jq -r --arg name "$name" '
    .[] | select((.name | ascii_downcase) == ($name | ascii_downcase)) | .name
  ' <<<"$options")
  [[ "$existing" != "$name" ]] || continue
  [[ -z "$existing" ]] || stop "Status '$existing' differs from '$name' only by case."
  echo "Missing status: $name"
  options=$(jq --argjson expected "$expected" '. + [$expected]' <<<"$options")
  missing=$((missing + 1))
done < <(jq -c '.statuses[]' "$baseline_file")

if ((missing > 0)) && [[ "$apply" == true ]]; then
  payload=$(jq -n --arg id "$(jq -r .id <<<"$status_field")" --argjson options "$options" '{
    query: "mutation($input: UpdateProjectV2FieldInput!) { updateProjectV2Field(input: $input) { projectV2Field { ... on ProjectV2SingleSelectField { id } } } }",
    variables: {input: {fieldId: $id, singleSelectOptions: $options}}
  }')
  result=$(gh api graphql --input - <<<"$payload")
  jq -e '.data.updateProjectV2Field != null and (.errors | length) == 0' <<<"$result" >/dev/null
  echo "Added $missing missing status options."
fi

read_labels() {
  gh api "repos/$repo/labels?per_page=100" --paginate --slurp | jq 'add // []'
}
labels=$(read_labels)
while IFS= read -r expected; do
  name=$(jq -r .name <<<"$expected")
  if jq -e --arg name "$name" 'any(.[]; (.name | ascii_downcase) == ($name | ascii_downcase))' <<<"$labels" >/dev/null; then
    continue
  fi
  echo "Missing label: $name"
  if [[ "$apply" == true ]]; then
    gh label create "$name" --repo "$repo" \
      --color "$(jq -r .color <<<"$expected")" --description "$(jq -r .description <<<"$expected")"
  fi
done < <(jq -c '.labels[]' "$baseline_file")

if [[ "$apply" == true ]]; then
  load_project
  labels=$(read_labels)
  jq -e --argjson field "$status_field" --argjson labels "$labels" '
    ([.statuses[].name] - [$field.options[].name] | length == 0) and
    ([.labels[].name | ascii_downcase] - [$labels[].name | ascii_downcase] | length == 0)
  ' "$baseline_file" >/dev/null
  repository=$(gh repo view "$repo" --json nameWithOwner,id,projectsV2)
  jq -e --arg id "$project_id" '
    (.projectsV2.Nodes | length) == 1 and .projectsV2.Nodes[0].id == $id
  ' <<<"$repository" >/dev/null
  echo 'Verified: required statuses, labels, and the one-to-one Project link are present.'
else
  echo 'Preview only. Nothing changed; add --apply to create missing configuration.'
fi
echo 'Manual checklist: disable built-in workflows; use Board layout with Status columns.'
echo 'Existing extra statuses and labels are preserved.'
