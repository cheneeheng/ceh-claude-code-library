# ceh-seo

Discoverability standards for anything exposed to the internet: SEO and GEO (generative engine
optimization) for public web pages, repo READMEs, package listings, and landing copy.

## Skills

Discoverability is one activity applied to many surfaces. The skills split on surface mechanics,
which is also where their trigger moments and file types are disjoint:

| Skill                        | Invoke                                | Triggers when                                                                                                                                            |
| ---------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `make-page-crawlable`        | `/ceh-seo:make-page-crawlable`        | Shipping or creating a public web page: per-page head checklist, sitemap/robots, JSON-LD structured data, SSR/prerender requirements, GEO rules          |
| `write-llms-txt`             | `/ceh-seo:write-llms-txt`             | Creating or updating the `llms.txt` reading list for AI agents: the positional format, link curation, `## Optional`, markdown over HTML, `llms-full.txt` |
| `write-project-listing-text` | `/ceh-seo:write-project-listing-text` | Writing the README first screen, package description and keywords, GitHub topics, marketplace listings, or landing copy: the excerpt rule and one-liner  |

Two skills carry a GEO layer: content structured so AI engines can extract and cite it —
answer-first sections, standalone quotable facts, question-shaped headings.

## Boundaries

- README **accuracy** after a code change belongs to `ceh-git-workflow:update-readme`. This plugin
  owns README **findability**.
- Writing the content itself (blog posts, docs) belongs to `ceh-blog` and `ceh-documentation`. This
  plugin governs how that content is found and cited.
- Accessibility always wins conflicts with SEO.
