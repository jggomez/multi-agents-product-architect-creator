import os
from datetime import datetime
from google.adk.tools import ToolContext
from google.genai import types


async def generate_report(tool_context: ToolContext = None) -> str:
    """Aggregates all pipeline artifacts into a single, consolidated final Markdown report.

    This is the LAST tool the Orchestrator should call, after both the
    requirements_pipeline and design_iteration_loop have completed successfully.
    It dynamically discovers all '.md' artifacts saved during the session
    (user_stories.md, adr_collection.md, ux_mockup.md, ux_feedback.md),
    merges them into a structured report with a table of contents, and
    persists the result as 'final_report.md'.

    Preconditions:
        - At least the requirements phase must have completed (user_stories.md
          and adr_collection.md should exist).
        - Ideally the design phase also completed (ux_mockup.md, ux_feedback.md).

    Returns:
        The full Markdown string of the generated report.
        The report is also saved as artifact 'final_report.md'.
    """
    report_title = "Design System and Architecture Final Report"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Premium Header Section (No emojis)
    combined_md = f"""# {report_title}

> [!IMPORTANT]
> This report aggregates the collective intelligence of the Multi-Agent Design Workflow. It serves as the single source of truth for the project's requirements, architectural constraints, and visual design.

## Project Metadata
- **Project Name:** Multi-Agent UX Design Workflow
- **Status:** Final Review
- **Generated On:** {current_date}
- **Orchestrator:** ADK Multi-Agent System

---

## Table of Contents
1. [Executive Summary](#executive-summary)
"""

    # Dynamic discovery logic
    # Get current session artifacts
    all_artifacts = await tool_context.list_artifacts()

    # Filter for markdown files, excluding the report itself and non-relevant files
    md_artifacts = [
        a
        for a in all_artifacts
        if a.name.endswith(".md") and a.name != "final_report.md"
    ]

    # Sort artifacts for consistent report structure
    md_artifacts.sort(key=lambda x: x.name)

    # Add items to Table of Contents
    for i, artifact in enumerate(md_artifacts, start=2):
        title = artifact.name.replace(".md", "").replace("_", " ").title()
        anchor = title.lower().replace(" ", "-")
        combined_md += f"{i}. [{title}](#{anchor})\n"

    combined_md += f"{len(md_artifacts) + 2}. [Conclusion](#conclusion)\n\n---\n\n"
    combined_md += """## Executive Summary <a name="executive-summary"></a>
This document provides a comprehensive overview of the design phase. We have successfully translated user needs into actionable stories, established robust architectural patterns through ADRs, and iterated on a high-fidelity design that meets all technical and aesthetic standards.

---
"""

    artifacts_found = 0

    for artifact_meta in md_artifacts:
        name = artifact_meta.name
        content_str = None

        try:
            # Load from current session only
            artifact = await tool_context.load_artifact(name)
            if artifact:
                if artifact.text:
                    content_str = artifact.text
                elif artifact.inline_data:
                    content_str = artifact.inline_data.data.decode("utf-8")
        except Exception as e:
            print(f"Error loading artifact {name}: {e}")
            continue

        if content_str:
            # Clean up the content (remove top-level headers)
            lines = content_str.split("\n")
            if lines and lines[0].startswith("# "):
                content_str = "\n".join(lines[1:])

            # Generate section title from filename
            title = name.replace(".md", "").replace("_", " ").title()
            anchor = title.lower().replace(" ", "-")

            combined_md += f"\n## {title} <a name='{anchor}'></a>\n\n"
            combined_md += content_str + "\n\n"
            artifacts_found += 1
            combined_md += "---\n"

    combined_md += """
## Conclusion <a name="conclusion"></a>
The design process has reached a stable state. All stakeholders (Analyst, Architect, and UX Designer) have aligned on the proposed solution, and the Critic agent has validated the approach against the project goals. This package is now ready for implementation.
"""

    # Save Markdown as artifact
    md_part = types.Part.from_text(text=combined_md)
    await tool_context.save_artifact("final_report.md", md_part)

    return combined_md
