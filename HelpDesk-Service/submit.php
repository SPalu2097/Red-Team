<?php
require 'config.php';
session_start();

$errors = [];

/*
  PUHASTAME SISENDID
*/
$nimi = trim($_POST['nimi'] ?? '');
$osakond = trim($_POST['osakond'] ?? '');
$kontakt = trim($_POST['kontakt'] ?? '');
$probleem = trim($_POST['probleem'] ?? '');

/*
  VALIDATSIOON
*/
if ($nimi === '') {
    $errors[] = "Nimi on kohustuslik";
}

if ($osakond === '') {
    $errors[] = "Osakond on kohustuslik";
}

if ($kontakt === '') {
    $errors[] = "Kontakt on kohustuslik";
} else {
    // kui sisaldab @ -> emaili kontroll
    if (strpos($kontakt, '@') !== false) {
        if (!filter_var($kontakt, FILTER_VALIDATE_EMAIL)) {
            $errors[] = "E-mail ei ole korrektne";
        }
    }
}

if ($probleem === '') {
    $errors[] = "Probleemi kirjeldus on kohustuslik";
}

/*
  KUI VEAD → TAGASI INDEXI
*/
if (!empty($errors)) {
    $_SESSION['form_errors'] = $errors;
    header("Location: index.php?page=home");
    exit;
}

/*
  SALVESTUS (SAMA LOOGIKA MIS SINUL)
*/
$stmt = $pdo->prepare("
    INSERT INTO tickets (nimi, osakond, kontakt, probleem, staatus)
    VALUES (?, ?, ?, ?, 'Uus')
");

$stmt->execute([
    $nimi,
    $osakond,
    $kontakt,
    $probleem
]);

/*
  TAGASI EDU TEATEGA
*/
header("Location: index.php?page=home&success=1");
exit;