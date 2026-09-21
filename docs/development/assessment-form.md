# Edit an assessment using form fields

The job page lets you change an interpretation without editing JSON. Start with
the supplied comment and code, then use the [field meanings](assessment-fields.md).

1. Change the **Issue statement**, dropdown choices and **Candidate rule**.
   Leave the candidate rule blank when none is justified.
2. Use **Add category**, **Add evidence quote** or **Add applicability limit**
   when you need another entry. Remove an unwanted row with its labelled button.
   These buttons return the unsaved form; they do not record a decision.
3. Copy evidence exactly from the supplied source. Choose **Comment** or **Code**
   for each quote. Empty list rows are ignored; all other whitespace is preserved.
4. Add your notes, including limitations and advice beyond the original comment.
5. Review the fields **in this tab**, then choose **Save edited assessment**.
   Changes are not shared with another tab and are lost on a fresh page load.
6. Check the saved **Human interpretation** and **Saved assessment notes**.
   A validation error leaves your entries available for correction; no decision
   is saved until validation succeeds.

| Decision button | What it saves |
| --- | --- |
| Save edited assessment | Your complete edited interpretation and notes |
| Accept original | The original model interpretation and your notes; edited fields are ignored |
| Reject | Your rejection and notes, without an edited interpretation |

Each decision saves immediately and cannot be overwritten. A failed model draft
offers correction or rejection only. If its structure cannot populate the form,
the original text remains available and the fields start without guessed choices.

## Submission and compatibility

- The form works without JavaScript. List buttons submit the current fields to
  render another unsaved form. They never call the annotation writer.
- The web adapter owns HTML field encoding. The existing annotation service owns
  eligibility, interpretation validation, exact evidence grounding and persistence.
- Browser-normalised quote line endings resolve to one exact source substring.
  Missing or ambiguous matches fail; whitespace is not otherwise relaxed.
- Existing open JSON forms remain accepted for compatibility. New pages use fields;
  JSON remains a read-only provenance view and the command-line edit format.
- There is no new schema, prompt version, model call, annotation state or store.
  A stale tab cannot replace a recorded decision. Keep a mistaken saved assessment
  as evidence and resolve its research disposition explicitly.
