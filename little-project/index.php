<?php
require 'config.php';
?>

<!DOCTYPE html>
<html lang="et">
<head>
<meta charset="UTF-8">
<title>IT Helpdesk</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">

    <a class="navbar-brand" href="index.php?page=home">Kasutajatugi</a>

    <div class="navbar-nav">
      <a class="nav-link" href="index.php?page=home">Avaleht</a>
      <a class="nav-link" href="index.php?page=kkk">KKK</a>
      <a class="nav-link" href="index.php?page=kontaktid">Kontaktid</a>
    </div>

    <div class="ms-auto">
      <a href="login.php" class="btn btn-outline-light btn-sm">
        Admin paneel
      </a>
    </div>

  </div>
</nav>

<div class="container mt-4">

<?php
$page = $_GET['page'] ?? 'home';
?>

<?php if ($page == 'home') { ?>

<h3>IT pöördumise vorm</h3>

<?php
// ERRORS
if (!empty($_SESSION['form_errors'])) {
    foreach ($_SESSION['form_errors'] as $error) {
        echo "<div class='alert alert-danger'>$error</div>";
    }
    unset($_SESSION['form_errors']);
}

// SUCCESS
if (isset($_GET['success'])) {
    echo "<div class='alert alert-success'>Päring edukalt saadetud!</div>";
}
?>

<form action="submit.php" method="post" class="mt-3">

<input class="form-control mb-2" name="nimi" placeholder="Nimi">
<input class="form-control mb-2" name="osakond" placeholder="Osakond">
<input class="form-control mb-2" name="kontakt" placeholder="E-mail või telefon">

<textarea class="form-control mb-2" name="probleem"
placeholder="Kirjelda oma probleem võimalikult täpselt..."></textarea>

<button class="btn btn-primary">Saada pöördumine</button>

</form>

<?php } ?>

<?php if ($page == 'kkk') { ?>

<h3>Korduma kippuvad küsimused (KKK)</h3>

<div class="card p-3">
<h5>Kuidas kirjeldada oma probleemi õigesti?</h5>

<ul>
<li>Kirjelda täpselt, mis ei tööta</li>
<li>Lisa veateade</li>
<li>Ütle seade</li>
<li>Kirjelda mida proovisid</li>
</ul>

</div>

<?php } ?>

<?php if ($page == 'kontaktid') { ?>

<h3>Kontaktid</h3>

<div class="card p-3">
<h5>IT tugi</h5>
<p>
<b>Simon Palu</b><br>
📧 simon.palu@omamure.ee
</p>
</div>

<?php } ?>

</div>

</body>
</html>