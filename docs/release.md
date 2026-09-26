# Release and publication

## Status

This directory holds a prepared publication candidate. A recorded,
independent review must approve every exported byte before publication.
The builder and local checks cannot grant that approval.

## Identity and inventory

The operator allocates a new empty public repository during publication.
The publication record captures its name, repository ID, and commit SHA.
This candidate contains no organization name or repository identity.

The manifest hashes six payload files. The manifest does not hash itself;
an approved external record must bind its exact bytes separately.

The workflow and actionlint configuration are generated. The README,
documentation, and release checker are retained source files.

## Reconstruct

1. Retrieve the approved internal source revision and retained files.
2. Run the builder from that source checkout.
3. Run the local release check:

       python3 tools/public_release.py --check

The check compares the two generated files with a fresh build. It also
verifies payload hashes, inventory, driver parity, and known forbidden
patterns. Those patterns are finite and cannot prove semantic safety.

## Publish

1. Review every exported byte and record the approval externally.
2. Record the approved payload hashes and exact manifest bytes.
3. Initialize a fresh public repository with no unrelated history.
4. Copy only the approved payload files and manifest into that repository.
5. Compare the prepared repository tree with the approved external record.
6. Run the declared local delivery gates.
7. Publish through normal repository policy without bypass.
8. Read the published commit and files through the provider.
9. Compare every published byte with the approved external record.
10. Stop further rollout and report any mismatch.

The operator must not reuse an internal repository's Git history or
publish an internal clone. The candidate's own mutable manifest cannot
serve as its independent approval record.

## Qualify the required gate

1. Obtain organization administration authority for the configuration.
2. Configure the candidate source in a controlled pilot or protected
   overlap.
3. Prove that the required workflow accepts a clean pull request.
4. Prove that the required workflow rejects a synthetic credential.
5. Bind each result to the required source repository, path, and revision.
6. Narrow incompatible old targeting only after the new source is proven.

A same-name ordinary workflow is not required-source identity proof.
The operator must preserve enforcement throughout the transition.
Mirror lint and local fixture results do not prove hosted enforcement.

## Verify a published checkout

Compare the checkout with the approved external record before executing
its checker. After that comparison, run:

    python3 scripts/check_release.py --check

The checker verifies payload consistency, not approval or provenance.
It rejects invalid manifest paths, hashes, types, and schemas. It also
rejects missing or unlisted files, links, and executable-bit mismatches.
Unreadable inventory refuses completion rather than disappearing.

The checker ignores only the checkout root's own Git metadata on disk.
Manifest payload paths may never name Git metadata. The source builder
rejects all Git metadata inside the publication candidate.

## Update

1. Change the builder, template, or retained sources through review.
2. Regenerate the workflow, actionlint configuration, and manifest.
3. Run the full local gate and release checks.
4. Review and approve the new exported bytes externally.
5. Repeat the publication and readback procedure above.
6. Qualify the candidate through a controlled required-workflow pilot.
7. Promote its revision to production requirements only after qualification.

Do not hand-edit generated files or publish unlisted files. Do not skip
external byte comparison, required review, or the required gate.
