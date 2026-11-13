---
schema: fix-record/v2
generated_from: workspace-checkpoint-recording-and-replay.yaml
generated_note: "Do not edit. artifact.py renders this file from workspace-checkpoint-recording-and-replay.yaml: edit the YAML, then run artifact.py render."
status: fixed
date: 2026-11-13
---

<!-- prettier-ignore-start -->

# Workspace checkpoints misread quoted commands, overwrite branch entries and repeat commits

**Symptom:** `python -m unittest discover -s tools/validate-plugins/tests -p test_workspace_checkpoints.py -v` → FAILED (failures=3, errors=2)

## Diagnosis

| Hypothesis | Refuted by | Result |
| --- | --- | --- |
| Raw separators split quoted subjects and match quoted merge mentions. | Quoted semicolons and pipes preserve real merges, and a printf argument creates no entry. | confirmed: Both quoted subjects raised No closing quotation; printf created a pending entry. |
| Replacing branch punctuation with underscores loses reference identity. | feat/a, feat_a, feat/b and feat_b create four distinct pending entries. | confirmed: AssertionError: 2 != 4 |
| A recent repeated merge event creates a checkpoint without consulting existing history. | Existing checkpoint history prevents another git commit for the same PR and merge commit. | confirmed: The mock command log showed git commit despite an existing checkpoint. |

**Cause:** plugins/standalone/ceh-git-workflow/scripts/sync-agents-workspace.py: pending_name, record_merge and checkpoints: Regex matching and splitting ran before shell quoting was interpreted. Branch-name
normalization mapped distinct references to the same filename. Consuming a pending
entry did not check whether the workspace already held that PR's checkpoint, so
replaying a merge event inside the recency window produced another empty commit.

**Prediction:** `python -m unittest discover -s tools/validate-plugins/tests -p test_workspace_checkpoints.py -v` → A pipe in a quoted subject also raised No closing quotation, and a second slash/underscore branch pair also collided.

## Fix

Split command segments outside quoted and escaped text before shlex tokenization.
Name branch pending files with the complete reference's SHA-256 digest, so punctuation,
case differences and long references cannot collide or exceed filename limits. Consult
existing checkpoint commit bodies before creating another checkpoint for the same merge.

**Tests:**

- `test_quoted_separator_in_subject_preserves_merge` — protects: A semicolon or pipe inside a quoted subject preserves the real merge command.; fails_when: A separator is treated as a command boundary before quoting is parsed.; why_new: Previous recording fixtures used subjects without separators.
- `test_quoted_merge_mention_is_not_a_command` — protects: A merge command mentioned inside a printf argument creates no pending entry.; fails_when: A separator inside quoted prose anchors a false command match.; why_new: The previous negative mention fixture contained no quoted separator.
- `test_distinct_branch_references_do_not_overwrite_each_other` — protects: Slash, underscore and case-only branch differences keep distinct pending entries.; fails_when: Filename normalization or filesystem case folding merges references.; why_new: Previous fixtures wrote only one branch reference at a time.
- `test_long_branch_reference_fits_a_pending_filename` — protects: A valid multi-component branch name fits a fixed-length pending filename.; fails_when: The whole encoded branch becomes one oversized filename.; why_new: Previous branch fixtures used short names.
- `test_repeated_merge_event_does_not_repeat_a_checkpoint` — protects: Existing checkpoint history clears a replay without another commit.; fails_when: The handler checks pending entries but never checks existing checkpoint history.; why_new: The previous repeat-Stop fixture did not recreate a consumed merge event.
- `tools/validate-plugins/checks/hooks.py recording and replay fixtures` — protects: The command-line hook exercises quoting, reference identity and replay using real local Git.; fails_when: The hook creates a false entry, overwrites a branch entry or repeats a checkpoint.; why_new: These cases were missing from the original planned integration fixtures.

**Unverified:** Live installed-hook behavior after a real GitHub merge remains unverified.

<!-- prettier-ignore-end -->
