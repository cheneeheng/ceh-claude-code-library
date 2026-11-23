#!/usr/bin/env bash
# Seeds a primitive orders page: inline styles, plain-text status, two filled buttons,
# and a Refresh button whose onclick names a function that does not exist.
set -euo pipefail
cat >orders.html <<'HTML'
<!DOCTYPE html>
<html>
<head>
<title>Orders</title>
<style>
body { font-family: Arial; text-align: center; background: #eeeeee; }
table { margin: 0 auto; border: 1px solid #000; }
td, th { border: 1px solid #000; padding: 5px; }
button { background: #0066ff; color: #fff; padding: 8px; }
</style>
</head>
<body>
<h1>Orders</h1>
<button onclick="refreshOrders()">Refresh</button>
<button onclick="alert('new')">New order</button>
<table>
<tr><th>#</th><th>Customer</th><th>Total</th><th>Status</th><th>Failed items</th></tr>
<tr><td>1</td><td>Acme GmbH</td><td>1200</td><td>shipped</td><td>0</td></tr>
<tr><td>2</td><td>Borealis Ltd</td><td>89.5</td><td>pending</td><td>0</td></tr>
<tr><td>3</td><td>Corvid &amp; Sons International Trading Company</td><td>15000</td><td>failed</td><td>2</td></tr>
</table>
<script>
function refreshOrder() { location.reload(); }
</script>
</body>
</html>
HTML
