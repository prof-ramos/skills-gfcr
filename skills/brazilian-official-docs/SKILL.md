---
name: brazilian-official-docs
description: Create and validate Brazilian official documents (ofícios, memorandos, pareceres, notas técnicas) following Brazilian government standards (Manual da Presidência, Manual do Itamaraty, ABNT). Use when creating formal government documents, validating document compliance with Brazilian norms, or needing reference material on Brazilian official writing standards. Includes LaTeX templates, Python generators, validators, and comprehensive reference documentation on Brazilian official communication standards.
---

# Brazilian Official Documents

Create and validate professional Brazilian government documents following official standards and best practices.

## Quick Start

**For document generation:**
1. Review `references/normas-brasileiras.md` for document type and formatting standards
2. Use `scripts/gerar_documento.py` with appropriate parameters
3. Output: Professionally formatted PDF following Brazilian government standards

**For document validation:**
1. Use `scripts/validar_documento.py <file>` to check compliance
2. Review errors and warnings
3. Apply corrections based on validation feedback

## Document Types Supported

### Ofício (Official Letter)
External formal communication between government agencies or to citizens.

**Key elements:**
- Header with agency name
- Document number: "Ofício nº XXX/YYYY-SIGLA"
- Date in full text format
- Complete recipient information
- Subject line
- Formal salutation (vocativo)
- Body text (2-6 lines per paragraph)
- Formal closing: "Atenciosamente," or "Respeitosamente,"
- Signature block

**Generate with:**
```python
from scripts.gerar_documento import DocumentGenerator

generator = DocumentGenerator()
generator.gerar_oficio(
    output_path='oficio.pdf',
    numero='123',
    destinatario={'nome': '...', 'cargo': '...', ...},
    assunto='...',
    corpo_texto=r'...',  # Use \par for paragraph breaks
    signatario={'nome': '...', 'cargo': '...'},
    orgao={'nome': '...', 'sigla': '...', 'cidade': '...'},
    fecho='Atenciosamente',  # or 'Respeitosamente' for higher authority
    vocativo='Senhor'  # or appropriate title
)
```

### Memorando (Internal Memo)
Internal communication between departments or officials within same agency.

**Key elements:**
- Simpler format than ofício
- Document number: "Memorando nº XXX/YYYY-SIGLA"
- Direct recipient (department/sector)
- No formal salutation
- Concise, objective content
- Signature block

**Generate with:**
```python
generator.gerar_memorando(
    output_path='memorando.pdf',
    numero='045',
    destinatario_setor='Coordenação de Recursos Humanos',
    assunto='...',
    corpo_texto=r'...',
    signatario={'nome': '...', 'cargo': '...'},
    orgao={'nome': '...', 'sigla': '...', 'cidade': '...'}
)
```

## Reference Material

`references/normas-brasileiras.md` contains comprehensive guidance on:

**Communication Standards:**
- Manual da Presidência da República guidelines
- Manual do Itamaraty (diplomatic communications)
- Language requirements (impessoalidade, clareza, concisão, formalidade)
- Pronomes de tratamento (forms of address) for all authority levels
- Proper closings based on recipient hierarchy

**Document Structures:**
- Complete formatting specs for 6+ document types
- ABNT formatting standards (margins, fonts, spacing)
- Paragraph and numbering conventions
- Date and number formatting rules

**Legal References:**
- Citation formats for laws, decrees, articles
- Proper abbreviations and terminology
- Latin expressions commonly used
- Official acronyms

**Load when:** Creating any Brazilian official document or needing clarification on standards.

## Templates

LaTeX templates in `assets/` directory:

- `template_oficio.tex` - Official letter template
- `template_memorando.tex` - Internal memo template

**Template structure:**
- Professional header/timbre area
- Proper margin/spacing following ABNT
- Placeholders marked as `{{VARIABLE_NAME}}`
- Automatic date formatting
- Signature block formatting

**Direct usage:**
1. Copy template
2. Replace placeholders
3. Compile with pdflatex

**Programmatic usage:**
Use `DocumentGenerator` class which handles template loading, placeholder replacement, and PDF compilation.

## Validation

`scripts/validar_documento.py` checks documents against Brazilian norms:

**Usage:**
```bash
python3 scripts/validar_documento.py documento.txt
```

**Validation checks:**
- Document numbering format
- Pronome de tratamento usage and verbal agreement
- Formal closing presence and correctness
- Paragraph length (flags >8 lines)
- Legal citation format
- Date format compliance
- First-person language detection
- Colloquial expressions
- Formatting issues (excessive whitespace)

**Output:**
- Errors (❌): Must fix for compliance
- Warnings (⚠️): Recommended improvements
- Success (✓): Document follows all standards

## Writing Guidelines

**Language principles:**
1. **Impessoalidade** - Avoid first person, use impersonal constructions
2. **Clareza** - Short sentences, common vocabulary, direct meaning
3. **Concisão** - Eliminate unnecessary words without losing clarity
4. **Formalidade** - Maintain professional tone appropriate to government communication
5. **Padrão culto** - Use standard/formal Portuguese grammar and vocabulary

**Pronomes de tratamento agreement:**
- Always third person: "Vossa Excelência **solicitou**" (never "solicitastes")
- Adjectives agree with person's gender: "Vossa Senhoria está **ocupado**" (for male)

**Hierarchy-appropriate closings:**
- "Respeitosamente," - To higher authorities
- "Atenciosamente," - To equal or lower rank

**Paragraph structure:**
- 2-6 lines per paragraph optimal
- 2-3 sentences per paragraph
- Avoid single paragraphs >8 lines

**Numbers:**
- 0-10: Write out (zero, um, dois, etc.)
- >10: Use digits
- Exception: Large round numbers (mil, milhão)
- Percentages: Always digits (15%)
- Money: Always digits (R$ 1.234,56)
- Legal acts: Always digits (Lei nº 8.112)

**Dates:**
- Full format: "13 de janeiro de 2025"
- Numeric: 13/01/2025 or 13.01.2025
- Never: 13-01-2025 in official documents

## Common Workflows

**Creating ofício from scratch:**
1. Determine document number (sequential for year)
2. Identify recipient authority level (determines vocativo/fecho)
3. Draft body text following paragraph guidelines
4. Review against normas-brasileiras.md
5. Generate using script or template
6. Validate output

**Converting draft to official format:**
1. Run validation on draft
2. Fix errors (numbering, pronouns, closing)
3. Apply formatting warnings (paragraph length, whitespace)
4. Check language for impessoalidade
5. Regenerate and validate

**Adapting for Itamaraty standards:**
- Use numbered paragraphs
- Employ more formal diplomatic language
- Include appropriate diplomatic protocol
- Reference specific sections in normas-brasileiras.md for MRE requirements

## Important Notes

**LaTeX compilation requirements:**
- Requires pdflatex in system PATH
- Scripts use 2-pass compilation (for cross-references)
- Temporary files created in system temp directory
- Check compilation logs if PDF generation fails

**Character encoding:**
- All files use UTF-8
- Templates support Brazilian Portuguese characters (ã, ç, etc.)
- Ensure input text is properly encoded

**Customization:**
- Templates can be modified for specific agency branding
- Add agency logos by modifying \timbre command in templates
- Adjust margins/spacing while maintaining ABNT compliance

**Validation limitations:**
- Heuristic-based (may have false positives/negatives)
- Does not check factual content accuracy
- Legal citation validation is pattern-based
- Manual review still recommended for critical documents
