# Claude Code Integration Test

This file demonstrates how Claude Code can interact with the AI Employee vault.

## Instructions for Testing

1. Place this entire project directory in Claude Code's workspace
2. Claude Code should be able to:
   - Read files in the AI_Employee_Vault directory
   - Process files in the Needs_Action folder
   - Update the Dashboard.md with new information
   - Move files from Needs_Action to Done after processing
   - Follow the rules defined in Company_Handbook.md

## Expected Claude Code Tasks

When Claude Code accesses this vault, it should be able to:

1. Read the Company_Handbook.md to understand operational rules
2. Check the Needs_Action folder for pending tasks
3. Process the TEST_Claude_Code_Integration.md file
4. Update Dashboard.md with processing information
5. Move processed files to the Done folder

## Verification

After Claude Code processes this vault:
- The TEST_Claude_Code_Integration.md file should be moved to the Done folder
- Dashboard.md should have an updated entry in the "Recent Activity" section
- The "Tasks Processed" counter in Dashboard.md should increment

This confirms that Claude Code can successfully read from and write to the vault as required by the Bronze Tier specification.