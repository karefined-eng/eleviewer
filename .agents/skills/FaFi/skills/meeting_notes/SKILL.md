---
name: meeting-notes
description: A skill to demonstrate output templates and example patterns for creating consistent meeting notes.
---

# Meeting Notes Skill

This skill helps you create structured and consistent meeting notes by providing flexible and strict template options. You can choose a template that best fits your needs.

## Commands

### `create-notes`

Creates a new meeting notes file from a template.

**Usage:**

```
create-notes --template <template_name> --output <output_file>
```

**Arguments:**

*   `--template`: The name of the template to use. Available templates are `simple` and `detailed`.
*   `--output`: The path to the output file.

## Templates

This skill provides two templates for meeting notes:

*   **simple**: A basic template with essential sections like attendees, agenda, and action items.
*   **detailed**: A comprehensive template with additional sections for discussion points, decisions, and next steps.

## Examples

**Create a simple meeting notes file:**

```
create-notes --template simple --output meeting_notes.md
```

**Create a detailed meeting notes file:**

```
create-notes --template detailed --output project_kickoff_notes.md
```
