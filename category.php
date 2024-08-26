<?php

@include 'config.php';

session_start();

$user_id = $_SESSION['user_id'];

if(!isset($user_id)){
   header('location:login.php');
};


?>

<!DOCTYPE html>
<html lang="en">
<head>
   <meta charset="UTF-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>category</title>

   <!-- font awesome cdn link  -->
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">

   <!-- custom css file link  -->
   <link rel="stylesheet" href="css/style.css">

</head>
<body>
   
<?php include 'header.php'; ?>

<section class="movies">

   <h1 class="title">Movies Categories</h1>

   <div class="box-container">

   <?php
      $category_name = $_GET['category'];
      $select_movies = $conn->prepare("SELECT * FROM `movies` WHERE category = ?");
      $select_movies->execute([$category_name]);
      if($select_movies->rowCount() > 0){
         while($fetch_movies = $select_movies->fetch(PDO::FETCH_ASSOC)){ 
   ?>
   <form action="" class="box" method="POST">
      <img src="uploaded_img/<?= $fetch_movies['image']; ?>" alt="">
      <div class="name"><?= $fetch_movies['name']; ?></div>
      <input type="hidden" name="pid" value="<?= $fetch_movies['id']; ?>">
      <input type="hidden" name="p_name" value="<?= $fetch_movies['name']; ?>">
      <input type="hidden" name="p_image" value="<?= $fetch_movies['image']; ?>">
   </form>
   <?php
         }
      }else{
         echo '<p class="empty">no Movies available!</p>';
      }
   ?>

   </div>

</section>







<?php include 'footer.php'; ?>

<script src="js/script.js"></script>

</body>
</html>