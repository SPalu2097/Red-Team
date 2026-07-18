<?php
require 'config.php';

if (!isset($_SESSION['admin'])) {
    header("Location: login.php");
    exit;
}

/*
  STATISTIKA
*/
$stats = [
    'uus' => $pdo->query("SELECT COUNT(*) FROM tickets WHERE staatus='Uus'")->fetchColumn(),
    'töös' => $pdo->query("SELECT COUNT(*) FROM tickets WHERE staatus='Töös'")->fetchColumn(),
    'lahendatud' => $pdo->query("SELECT COUNT(*) FROM tickets WHERE staatus='Lahendatud'")->fetchColumn()
];

/*
  OTSING
*/
$search = $_GET['search'] ?? '';

if ($search) {
    $stmt = $pdo->prepare("
        SELECT * FROM tickets
        WHERE nimi LIKE ?
        OR kontakt LIKE ?
        OR probleem LIKE ?
        ORDER BY id DESC
    ");

    $stmt->execute([
        "%$search%",
        "%$search%",
        "%$search%"
    ]);
} else {
    $stmt = $pdo->query("
        SELECT * FROM tickets
        ORDER BY id DESC
    ");
}

$tickets = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!doctype html>
<html lang="et">
<head>
<meta charset="utf-8">
<title>Admin Paneel</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

<style>
body {
    background: #f4f6f9;
}

.card-counter {
    border: none;
    border-radius: 15px;
}

.table {
    background: white;
}
</style>

</head>
<body>

<nav class="navbar navbar-dark bg-dark shadow">
    <div class="container">
        <span class="navbar-brand">Admin Paneel</span>

        <div class="text-white">
            Tere, <?= htmlspecialchars($_SESSION['username'] ?? 'Admin') ?>
        </div>

        <a href="logout.php" class="btn btn-outline-light btn-sm">
            Logi välja
        </a>
    </div>
</nav>

<div class="container mt-4">

<!-- STATISTIKA -->
<div class="row mb-4">

    <div class="col-md-4">
        <div class="card bg-danger text-white card-counter p-3">
            <h5>Uued</h5>
            <h2><?= $stats['uus'] ?></h2>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card bg-warning card-counter p-3">
            <h5>Töös</h5>
            <h2><?= $stats['töös'] ?></h2>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card bg-success text-white card-counter p-3">
            <h5>Lahendatud</h5>
            <h2><?= $stats['lahendatud'] ?></h2>
        </div>
    </div>

</div>

<!-- OTSING -->
<div class="card shadow mb-3">
    <div class="card-body">
        <form method="get" class="row g-2">
            <div class="col">
                <input type="text" name="search"
                       value="<?= htmlspecialchars($search) ?>"
                       class="form-control"
                       placeholder="Otsi nime, kontakti või probleemi järgi">
            </div>
            <div class="col-auto">
                <button class="btn btn-dark">Otsi</button>
            </div>
            <div class="col-auto">
                <a href="admin.php" class="btn btn-secondary">Tühjenda</a>
            </div>
        </form>
    </div>
</div>

<!-- TABEL -->
<div class="card shadow">
<div class="card-body p-0">

<table class="table table-hover mb-0">

<thead class="table-dark">
<tr>
    <th>#</th>
    <th>Nimi</th>
    <th>Kontakt</th>
    <th>Probleem</th>
    <th>Staatus</th>
    <th>Tegevus</th>
</tr>
</thead>

<tbody>

<?php if(empty($tickets)): ?>
<tr>
    <td colspan="6" class="text-center py-4">
        Päringuid ei leitud
    </td>
</tr>
<?php endif; ?>

<?php foreach($tickets as $row): ?>

<tr>
    <td><?= $row['id'] ?></td>

    <td><?= htmlspecialchars($row['nimi']) ?></td>

    <td><?= htmlspecialchars($row['kontakt']) ?></td>

    <td><?= htmlspecialchars($row['probleem']) ?></td>

    <td>
        <?php
        $colors = [
            'Uus' => 'danger',
            'Töös' => 'warning',
            'Lahendatud' => 'success'
        ];

        $color = $colors[$row['staatus']] ?? 'secondary';
        ?>
        <span class="badge bg-<?= $color ?>">
            <?= htmlspecialchars($row['staatus']) ?>
        </span>
    </td>

    <td>

        <?php if($row['staatus'] == 'Uus'): ?>
            <a href="staatus.php?id=<?= $row['id'] ?>"
               class="btn btn-warning btn-sm">
                Alusta tööd
            </a>

        <?php elseif($row['staatus'] == 'Töös'): ?>
            <a href="staatus.php?id=<?= $row['id'] ?>"
               class="btn btn-success btn-sm">
                Märgi lahendatuks
            </a>

        <?php else: ?>
            <span class="text-success fw-bold">✓ Valmis</span>
        <?php endif; ?>

        <a href="kustuta.php?id=<?= $row['id'] ?>"
           class="btn btn-danger btn-sm"
           onclick="return confirm('Kas oled kindel?')">
            Kustuta
        </a>

    </td>
</tr>

<?php endforeach; ?>

</tbody>

</table>

</div>
</div>

</div>

</body>
</html>