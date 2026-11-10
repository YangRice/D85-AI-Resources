# Canonical Toastmasters Terminology Consolidation

Date: 2026-11-11

## Objective

Make one reviewed Toastmasters glossary the authoritative source for English-to-Chinese terminology throughout the repository, while preserving independently installable skills, generated portable prompts, and usable GitHub URLs.

## Scope

- Consolidate the duplicated core glossaries currently stored under the poster, PowerPoint, PDF, and speech-mentor skills.
- Preserve PDF-specific Pathways terms as a separate supplement.
- Make `Club Officer` consistently translate to the glossary's default `俱乐部官员`; remove conflicting `干部` and `干事` uses where they mean `Club Officer` in the Successful Club package.
- Update skill instructions and generated portable prompts that consume the glossary.
- Add generation and validation coverage so drift is detected automatically.
- Keep internal design and validation notes out of the public commit.

## Source of Truth

Create a neutral canonical file at:

`references/toastmasters-terminology.md`

The canonical file is the only hand-edited core glossary. Its context rule will be generalized from poster-specific language to any translated deliverable.

The PDF-specific Pathways material remains a separate hand-edited supplement within the PDF skill because it adds terms rather than replacing the core glossary.

## Distribution Model

Do not use filesystem symlinks. Symlinks are reliable in a complete local checkout but are not a safe interface for raw URLs, ZIP downloads, single-skill installation, or clients that do not preserve the target.

Maintain skill-local glossary files as generated mirrors where a skill must remain self-contained. The existing prompt-generation workflow will copy the canonical content into those declared skill-local references before portable prompts are built. Each generated mirror will carry a short generated-source notice.

Skill instructions continue linking to their local `references/toastmasters-terminology.md`, so local packages and stable GitHub blob URLs keep working. The canonical root file is also directly linkable for repository-wide review.

## Generator and Validator Interface

Add one explicit manifest or script-owned mapping from the canonical glossary to the skill-local mirror paths. The interface is:

- one canonical input path;
- a reviewed list of generated destinations;
- a check mode that reports drift without writing;
- a sync mode used before prompt generation.

The existing portable prompt builder reads the generated local files through the normal `portable_references` mechanism. It must not depend on browsing the canonical URL at runtime.

Repository validation will verify:

1. every declared mirror exactly matches the canonical content apart from its generated notice;
2. no mirror is hand-maintained independently;
3. each skill reference link resolves;
4. regenerated portable prompts contain the canonical glossary when declared;
5. Successful Club Chinese content uses `俱乐部官员` when the English concept is `Club Officer` and contains no conflicting `干部` or `干事` for that concept.

## Migration

1. Add the neutral canonical glossary using the currently approved terms.
2. Generalize its context sentence so it applies to posters, presentations, documents, and coaching output.
3. Replace duplicate core glossaries with generated mirrors.
4. Split the PDF file into the generated core glossary plus its existing Pathways supplement, or make the PDF skill load both local files explicitly.
5. Update the speech-mentor skill to use the generated core glossary without its speech-specific duplicated preamble.
6. Update catalog declarations so portable prompts embed required terminology references.
7. Correct Successful Club Chinese source files and regenerate its portable prompt.
8. Update README tree/documentation only where needed to describe the canonical and generated files.

## Error Handling

- Missing canonical input: fail generation with the exact path.
- Missing or undeclared destination: fail validation.
- Drifted generated mirror: fail validation and instruct maintainers to run the sync command.
- Escaping destination path or symlink destination: fail before reading or writing.
- Conflicting glossary default in tested Chinese source: fail with file and term.

## Verification

- Add failing tests first for glossary synchronization, link resolution, portable embedding, and `Club Officer` terminology.
- Run the glossary sync and inspect every generated change.
- Run all repository checks from `AGENTS.md`, the base-to-head safety scan, and whitespace checks.
- Run fresh realistic and missing-capability trials for any changed skill or portable-prompt behavior.
- Inspect outgoing history and public files before pushing.

## Public Commit Boundary

The public commit contains only this design specification (`design/toastmasters-terminology-consolidation.md`), the canonical glossary, generated mirrors, affected skill/catalog/generator/test files, regenerated prompts, and minimal public documentation. Behavioral evidence notes remain outside the repository.
