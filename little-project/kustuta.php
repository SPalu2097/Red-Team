<?php
require 'config.php';

if (!isset($_GET['id'])) {
    header("Location: admin.php");
    exit;
}

$id = (int) $_GET['id'];

$stmt = $pdo->prepare("DELETE FROM tickets WHERE id = ?");
$stmt->execute([$id]);

header("Location: admin.php");
exit;