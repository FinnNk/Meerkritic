# App bot responses to owner feedback

This convention applies only to `meerkritic-agent[bot]`, acting through the
Meerkritic GitHub App, when handling comments from the project owner (`FinnNk`).
It does not impose a reaction convention on human contributors or other identities.

Apply it wherever the owner's feedback occurs: PR conversation comments, review
summaries, inline review comments and their replies, and commit comments. Include
feedback on outdated diffs or older commits when reading it; do not limit attention
to the current PR conversation view.

1. **After reading a comment, add 👀 to that comment.** It acknowledges that the
   bot has read it; it does not imply agreement or completed work.
2. **If agreeing, even partly, and intending to revise, also add 👍 and reply.**
   State what is accepted and what will change before starting those revisions.
   For partial agreement, identify the accepted part and explain the remainder.
3. **Otherwise, leave an explanatory reply.** Explain why no revisions are planned,
   whether the point is disputed, already addressed, needs clarification or cannot
   be acted on. Retain 👀; do not add 👍 merely to acknowledge receipt.

Reply in the original thread where GitHub supports it. Otherwise, reply on the
associated PR or commit and link the original comment so the response is traceable.
Check the bot's existing reactions and replies to avoid duplicate acknowledgements.
If the assessment changes, explain the new disposition in a follow-up reply.

Use only the App's authentication for reactions and replies. These requested
acknowledgements do not require a fresh permission question each time. If a particular
GitHub surface or the App's permissions prevent the reaction or reply, explain that
limitation in an available reply location or report it to the owner; do not silently
skip it, claim success or substitute the owner's credentials.

For API clients, GitHub's reaction values are `eyes` for 👀 and `+1` for 👍. Select
the endpoint or supported GraphQL operation for the actual comment type rather than
assuming every comment is a PR conversation comment. See the
[GitHub reactions reference](https://docs.github.com/en/rest/reactions/reactions).

These reactions and replies express reading and revision intent. They are not a
GitHub review approval, completed verification, thread resolution or merge authority.
Existing implementation, DER and owner-merge requirements still apply.
