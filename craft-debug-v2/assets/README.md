# Assets Directory

This directory contains files that are **used in output** - NOT loaded into context.

## What Goes Here?

### Templates
Files that get copied or modified to create final output:
- Document templates: `.docx`, `.pptx`, `.pdf`
- Code boilerplate: Starter projects, directory structures
- Configuration templates: `.yaml`, `.json`, `.toml`

### Visual Assets
Images, icons, and graphics used in generated content:
- Logos: `.png`, `.svg`
- Icons: `.ico`, `.svg`
- Diagrams: `.png`, `.jpg`, `.svg`

### Fonts
Typography files for document generation:
- Font files: `.ttf`, `.otf`, `.woff`, `.woff2`

### Data Files
Sample or seed data (not documentation):
- Sample datasets: `.csv`, `.json`, `.xml`
- Test fixtures: Example inputs for testing
- Seed data: Initial data for databases

## What Does NOT Go Here?

❌ **Documentation** → Use `references/` instead  
❌ **Executable code** → Use `scripts/` instead  
❌ **Instructions** → Put in `SKILL.md`

## Examples from Other Skills

### Brand Guidelines Skill
```
assets/
├── logo.png              # Company logo
├── slides_template.pptx  # PowerPoint template
└── brand_colors.json     # Color palette data
```

### Frontend Builder Skill
```
assets/
└── react-starter/        # Boilerplate React project
    ├── package.json
    ├── src/
    │   ├── App.jsx
    │   └── index.js
    └── public/
        └── index.html
```

### Document Generator Skill
```
assets/
├── contract_template.docx
├── invoice_template.xlsx
└── fonts/
    ├── roboto-regular.ttf
    └── roboto-bold.ttf
```

## How Agents Use Assets

Agents typically:
1. **Copy** the asset to a new location
2. **Modify** it based on user input (fill template fields, replace placeholders)
3. **Return** the modified file to the user

Assets are **never loaded into context** - they're treated as binary blobs that get manipulated.

## Tips

- Keep assets organized in subdirectories if many files
- Use descriptive names: `invoice_template.xlsx` not `template1.xlsx`
- Include a comment in SKILL.md about what assets exist
- Remove this README if you don't use assets (not every skill needs them)
