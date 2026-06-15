<?php
$log_file      = __DIR__ . '/clicks.log';
$redirect_file = __DIR__ . '/redirects.txt';

$map = [];
if (file_exists($redirect_file)) {
    foreach (file($redirect_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        if ($line === '' || $line[0] === '#') continue;
        [$s, $dest] = preg_split('/\s+/', $line, 2);
        $map[$s] = $dest;
    }
}

$stats = [];
foreach (array_keys($map) as $slug) {
    $stats[$slug] = ['count' => 0, 'first' => null, 'last' => null];
}

if (file_exists($log_file)) {
    foreach (file($log_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        $parts = explode("\t", $line, 2);
        if (count($parts) !== 2) continue;
        [$slug, $ts] = $parts;
        if (!isset($stats[$slug])) {
            $stats[$slug] = ['count' => 0, 'first' => null, 'last' => null];
        }
        $stats[$slug]['count']++;
        if ($stats[$slug]['first'] === null) $stats[$slug]['first'] = $ts;
        $stats[$slug]['last'] = $ts;
    }
}

uasort($stats, fn($a, $b) => $b['count'] <=> $a['count']);

$total_clicks = array_sum(array_column($stats, 'count'));
?><!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirect stats</title>
<style>
  body { font-family: monospace; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: .35rem .75rem; border-bottom: 1px solid #ddd; }
  th { background: #f4f4f4; }
  td.num { text-align: right; }
  .dest { color: #555; font-size: .85em; word-break: break-all; }
  .zero { color: #aaa; }
</style>
</head>
<body>
<h2>Redirect stats</h2>
<p><?= count($map) ?> redirect<?= count($map) !== 1 ? 's' : '' ?> &mdash; <?= $total_clicks ?> total click<?= $total_clicks !== 1 ? 's' : '' ?></p>
<table>
<tr><th>Slug</th><th>Destination</th><th class="num">Clicks</th><th>First</th><th>Last</th></tr>
<?php foreach ($stats as $slug => $d): ?>
<tr class="<?= $d['count'] === 0 ? 'zero' : '' ?>">
  <td><?= htmlspecialchars($slug) ?></td>
  <td class="dest"><?= htmlspecialchars($map[$slug] ?? '') ?></td>
  <td class="num"><?= $d['count'] ?></td>
  <td><?= htmlspecialchars($d['first'] ?? '') ?></td>
  <td><?= htmlspecialchars($d['last'] ?? '') ?></td>
</tr>
<?php endforeach; ?>
</table>
</body>
</html>
