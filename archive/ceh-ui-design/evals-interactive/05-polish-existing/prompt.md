---
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

this page looks amateur, polish it. save the polished version as dashboard.html

```html
<html>
  <head>
    <style>
      body {
        font-family: Arial;
        text-align: center;
        background: linear-gradient(#6a11cb, #2575fc);
        color: white;
      }
      .box {
        border: 1px solid #ccc;
        padding: 10px;
        margin: 10px;
        background: rgba(255, 255, 255, 0.2);
      }
      button {
        background: #2575fc;
        color: white;
        padding: 10px 20px;
        border: none;
      }
    </style>
  </head>
  <body>
    <div class="box">
      <a href="#">🚀 Dashboard</a> | <a href="#">📊 Projects</a> |
      <a href="#">⚙️ Settings</a>
    </div>
    <h1>Dashboard</h1>
    <div class="box"><button>New project</button> <button>Import</button></div>
    <div class="box">
      <table border="1">
        <tr>
          <th>#</th>
          <th>Name</th>
          <th>Owner</th>
          <th>Status</th>
          <th>Failed</th>
        </tr>
        <tr>
          <td>1</td>
          <td>Website redesign</td>
          <td>Mara</td>
          <td>✅ done</td>
          <td>0</td>
        </tr>
        <tr>
          <td>2</td>
          <td>Billing migration</td>
          <td>Tomas</td>
          <td>running</td>
          <td>2</td>
        </tr>
        <tr>
          <td>3</td>
          <td>Mobile app v2</td>
          <td>Lin</td>
          <td>❌ failed</td>
          <td>5</td>
        </tr>
        <tr>
          <td>4</td>
          <td>Data warehouse</td>
          <td>Priya</td>
          <td>draft</td>
          <td>0</td>
        </tr>
      </table>
    </div>
  </body>
</html>
```
