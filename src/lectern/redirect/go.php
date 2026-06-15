<?php
$slug = preg_replace('/[^a-z0-9_-]/i', '', $_GET['s'] ?? '');
$map  = [];
foreach (file(__DIR__.'/redirects.txt', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
    if ($line === '' || $line[0] === '#') continue;
    [$s, $dest] = preg_split('/\s+/', $line, 2);
    $map[$s] = $dest;
}
if (!isset($map[$slug])) { http_response_code(404); exit('Not found'); }

file_put_contents(__DIR__.'/clicks.log', $slug."\t".date('c')."\n", FILE_APPEND | LOCK_EX);
header('Location: '.$map[$slug], true, 302);
exit;
?>
