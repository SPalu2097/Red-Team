<?php
require 'config.php';

$id = (int)$_GET['id'];

/*
  ÕIGE veerg on: staatus
*/
$stmt = $pdo->prepare("SELECT staatus FROM tickets WHERE id=?");
$stmt->execute([$id]);

$currentStatus = $stmt->fetchColumn();

/*
  Staatuse loogika
*/
if ($currentStatus == 'Uus') {
    $newStatus = 'Töös';
}
elseif ($currentStatus == 'Töös') {
    $newStatus = 'Lahendatud';
}
else {
    $newStatus = 'Lahendatud';
}

/*
  UPDATE ÕIGE VEERUGA
*/
$stmt = $pdo->prepare("
    UPDATE tickets
    SET staatus=?
    WHERE id=?
");

$stmt->execute([$newStatus, $id]);

header("Location: admin.php");
exit;