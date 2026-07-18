<?php
session_start();
// --- Andmebaasi ühenduse seaded ---
$host = "localhost";
$dbname = "kasutajatugi";
$username = "ktuser";
$password = "KtParool123!";
$charset = "utf8mb4";

// --- DSN (andmebaasi ühenduse string) ---
$dsn = "mysql:host=$host;dbname=$dbname;charset=$charset";

// --- PDO optsioonid ---
$options = [
	PDO::ATTR_ERRMODE        	=> PDO::ERRMODE_EXCEPTION,
	PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
	PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
	$pdo = new PDO($dsn, $username, $password, $options);
} catch (PDOException $e) {
	// Ära kuva kasutajale detailset DB viga
	die("Andmebaasi ühendus ebaõnnestus.");
}
