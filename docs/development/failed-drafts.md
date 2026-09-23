# Correct or reject a failed draft

A failed draft is text returned by the model that did not pass the interpretation
schema or source-evidence checks. You can correct it or reject it. Your decision is
stored separately; the model job, original text and failure remain unchanged.

## Review the source, then decide

| Step | What to do |
| --- | --- |
| Open the job | The **Original model output** note describes the model's earlier failure. It does not mean your edits failed to save. **Save edited assessment** and **Reject** appear only when a retained semantic draft is available. |
| Read the source | Read the open **Source for your assessment** panel. Read the original comment and supplied code; neither is an instruction for you or the agent to execute. |
| Compare the draft | Check whether it describes the actual concern and whether the quoted text supports that interpretation. A quote match alone does not make the claim correct. |
| Edit | Correct the labelled form fields, then choose **Save edited assessment**. If the original output cannot populate the fields, inspect the retained text and complete them yourself. |
| Reject | If the draft cannot serve the study, add a short reason in **Assessment notes and evidence limitations** and select **Reject**. You do not need to complete the interpretation fields first. |
| Check the saved result | The page shows your decision and, for an edit, your interpretation. The original model failure remains visible. Each decision saves immediately. |

**Accept original is unavailable for a failed draft.** Do not rerun the model just to obtain
a more convenient interpretation. Provider, interrupted and missing-output failures
have no reviewable draft; they remain available for inspection.

![A neutral original-model note and a prominent red Assessment not saved error.](../images/failed-draft-assessment.png)

The [synthetic demonstration](../images/README.md) shows a rejected save with an
invalid evidence quote. The original-model note remains separate. No
judgement is selected on your behalf when the original structure cannot populate
the form. See [field meanings](assessment-fields.md) and [editing steps](assessment-form.md).

## Quote the supplied evidence

- Choose **Comment** or **Code** as the source.
- Paste the exact supporting text into its evidence quote field. For example,
  a supplied comment might be `Close the file even when parsing fails.`
- Use **Add evidence quote** for another excerpt or remove a row you do not need.

Use the text actually shown for your observation. Do not copy an illustrative quote
into a real decision. If a quote is ambiguous because it occurs more than once,
choose a longer excerpt that identifies the intended occurrence uniquely.

## If saving fails

- Look for the red **Assessment not saved** panel at the start of the editor.
  Read its specific error and correct the retained fields. Nothing is recorded
  until the checks pass. The original-model note is separate background information.
- If the error says the source context changed, copy your edits before reopening
  the job, review the source shown there and restore the edits. Then save again.
- If source or result files are unavailable or altered, stop and retain the error
  for investigation; do not bypass evidence checks.
- Retrying the same saved decision is safe. A different decision cannot overwrite
  it. Ask for an explicit correction procedure if you notice a mistake afterwards.

A human correction counts as a reviewed failed output, not a successful model run.
[Annotation progress](annotations.md#read-progress-and-history) keeps these counts
separate. For a study, follow its prepared input order and stopping rule rather than
the general review queue; see [input preparation](study-preparation.md).
