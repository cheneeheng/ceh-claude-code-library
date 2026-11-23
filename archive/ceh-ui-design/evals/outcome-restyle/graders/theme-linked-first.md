---
type: regex
pattern: '<head>(?:(?!<style|<link)[\s\S])*<link[^>]+brand\.css'
flags: i
target: { source: file, path: orders.html }
---
