# Reproduce the documentation screenshots

The screenshots show the real application with a small **synthetic demonstration**.
The comments, code, interpretations, decisions, vectors and rule were prepared for
illustration. No model was invoked and no human research judgement was collected.
The application's normal fixture labels remain visible where it provides them.

## Prepare a fresh demonstration

Use Python 3.12 and run these commands from the repository root. Choose a **new**
local directory outside every Git worktree; the script refuses an existing path.
It creates four source records, four prepared interpretations, one failed draft, three synthetic
decisions, a fixture selection, one group, one candidate and a saved review draft.

1. Install the locked dependencies:

   ```text
   uv sync --locked
   ```

2. Create the demonstration runtime:

   ```text
   uv run --locked python docs/images/create_demo.py --data-root ../extras/screenshot-demo
   ```

3. Serve it on a separate port:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/screenshot-demo serve --port 8006
   ```

4. Open `http://127.0.0.1:8006` and use the paths printed by the script or saved in
   `<data-root>/screenshot-routes.json`. Do not start a model server or worker.
5. For the guidance screenshot, enter **Documentation fixture** as the name and
   **Clarify the ownership-transfer exception.** as the instruction. Check the
   rule and its discussion message. Leave the form unsubmitted.
6. Capture the views below, crop to the relevant content and inspect the result
   in its guide. Stop the temporary web server when finished.

The fixture has repeatable content, but generated IDs, timestamps and derived
digests vary. Use the newly printed routes rather than copying IDs from an image.
The deliberately invalid source URL is a label for locally supplied bytes; the
script pre-populates the source and does not download from it. The rule's declared
author is **Documentation fixture**; it is not an assertion of human authorship.

## Capture record

Captured on **20 September 2026**, using application code at `da3e48c`, with no
application-source changes during capture. The fixture is [create_demo.py](create_demo.py)
in this documentation revision. The browser was the Codex in-app browser on Windows,
using its existing dark appearance, a reported 1280 × 720 CSS viewport and native
1265 × 712 pixel captures. Browser scaling can differ on another machine.

Only pixel crops were applied: no scaling, redaction, compositing or content edits.
Raw captures and runtime files remain outside Git. [captures.json](captures.json)
and [the correction captures](captures-draft-repair.json) record earlier pixel crop rectangles, scroll positions, image dimensions and SHA-256 hashes.
The [assessment clarity captures](captures-assessment-clarity.json) supersede the
result, assessment and failed-draft entries and add the source panel.
The [assessment form captures](captures-assessment-form.json), taken on
21 September 2026 from code at `f2993a8` (failed-draft wording refreshed at
`8f8b0c7`), replace the assessment and failed-draft
images and add the save controls. They use the same synthetic fixture in a fresh
runtime, the normal 1280 × 720 CSS viewport and 1232-pixel-wide crops. The long
form is shown in two focused views; no fields were hidden to fit it into one image.
Use the visible landmarks below when different browser scaling makes those exact
coordinates unsuitable. A crop must keep the relevant labels and controls readable.

The failed-draft image was refreshed on 23 September 2026 for the validation-notice
change, using the same synthetic fixture and the in-app browser's default dark
appearance. Open `failed_annotation` and choose **Save edited assessment** with
its deliberately invalid quote unchanged. The save must be rejected. Capture the
complete neutral note and red error panel; no assessment is created. The focused
478 × 215 crop supersedes that asset's older capture record; see
[validation-notice capture details](captures-validation-notices.json).

| Asset | Route key | Type / pixels | Content to retain |
| --- | --- | --- | --- |
| [Source browser](source-browser.png) | `observations` | Overview, 1232 × 675 | Dataset title, synthetic label, comment/code pair and Normalise action |
| [Assessment source](assessment-source.png) | `annotation` | Panel, 960 × 431 | Open source panel, synthetic origin, comment and code |
| [Interpretation result](annotation-result.png) | `annotation` | Panel, 960 × 507 | Proposed issue, impact scope, candidate rule and quoted evidence |
| [Assessment fields](annotation-assessment.png) | `annotation` | Panel, 1232 × 429 | Editor heading, issue text and judgement dropdowns |
| [Assessment save](assessment-save.png) | `annotation` | Panel, 1232 × 338 | Notes, immediate-save explanation and all three decision buttons |
| [Failed draft](failed-draft-assessment.png) | `failed_annotation` | Panel, 478 × 215 | Neutral original-model note and red failed-save error |
| [Saved selection](frozen-selection.png) | `selection` | Overview, 1232 × 605 | Fixture label, totals, queue action and complete first input card |
| [Discovery group](discovery-group.png) | `discovery` | Overview, 1232 × 514 | Result heading, fixture label, totals and complete representative card |
| [Rule definition](rule-definition.png) | `rule` | Panel, 960 × 391 | Title, fixture label, pending state, scope and exclusions |
| [Saved review draft](saved-review-draft.png) | `workspace` | Overview, 1232 × 482 | Saved status, pending rule, intent and separate Save/Apply controls |
| [Guidance selection](guidance-selection.png) | `guidance` | Overview, 1232 × 452 | Heading, selected rule/message and explicit submission button |

There are two crop widths: 1232 pixels for views containing wide cards or paired
columns, and 960 pixels for focused panels. Heights follow the content. Reuse these
assets across documents instead of making separate copies for each guide.

The source-browser image appears in the README and dataset guide. The assessment
panel is shared by the annotation and study-preparation guides. The study has no
group-rating interface yet; the discovery image must not be described as one.

## Maintain the images

The [navigation capture](harness-navigation.png) shows the shared header and assessment links from code at `cb3957a`, captured on 21 September 2026. [Its record](captures-navigation.json) gives the 1280 × 720 CSS viewport and 1232 × 129 pixel crop. Reuse the synthetic fixture and capture the top of an assessment page without scrolling. The earlier overview images start below the header and remain applicable; focused assessment images also exclude navigation.

The [preserved-source capture](preserved-source.png) supersedes the source-panel
illustration for the current assessment guide. It shows additional context above
the model input; the earlier capture remains a historical asset.

1. Follow the existing fixture setup with a fresh external directory, adding
   `--preserved-source` to `create_demo.py`.
2. Open its `annotation` route. The response and receipt are synthetic; their URLs
   are illustrative and no GitHub request is made.
3. Capture the source panel with the preserved identity collapsed. Keep the
   synthetic origin, retrieval label, difference labels and model-input heading.

[Capture metadata](captures-source-reading.json) records the application revision,
fixture hash, viewport, scroll and native pixel crop. The 1232 by 656 pixel image
uses the existing wide-panel width. Other field-editor screenshots remain current.

- Follow the [screenshot guidance](../development/documentation-style.md#screenshots-that-help-readers-act).
- Recapture affected views when controls, labels or behaviour change. Update the
  image, crop/hash record, alt text and caption together.
- Review the image at the document's displayed width, with the original available
  for closer inspection. Crop surrounding navigation before shrinking text.
- In PRs, use an immutable image URL from the reviewed commit and link these notes.
  Keep routine validation evidence separate from the illustration.

The assessment clarity images were captured on 20 September 2026 using application
code at `5efdc2e`, with a 1000 × 720 CSS viewport during responsive checks. Native
captures were cropped to the existing 960-pixel panel width. The viewport override
was reset afterwards. The failed editor was collapsed manually for the image; it
opens by default. No decision was saved during these captures.

The other original captures remain current. Earlier correction verification used a
separate synthetic job and saved one correction; neither demonstration is research data.
