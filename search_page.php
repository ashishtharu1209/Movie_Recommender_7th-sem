<?php

@include 'config.php';

session_start();

$user_id = $_SESSION['user_id'];

if (!isset($user_id)) {
   header('location:login.php');
}
;


?>

<!DOCTYPE html>
<html lang="en">

<head>
   <meta charset="UTF-8">
   <meta http-equiv="X-UA-Compatible" content="IE=edge">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>🔍𝚂𝚎𝚊𝚛𝚌𝚑</title>

   <!-- font awesome cdn link  -->
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css">

   <!-- custom css file link  -->
   <link rel="stylesheet" href="css/style.css">

</head>

<body>

   <?php include 'header.php'; ?>

   <section class="search-form">

      <form action="" method="POST">
         <input type="text" class="box" name="search_box" placeholder="search Movies...">
         <input type="submit" name="search_btn" value="search" class="btn">
      </form>

   </section>

   <?php



   ?>

   <section class="movies" style="padding-top: 0; min-height:100vh;">

      <div class="box-container">

         <?php
         if (isset($_POST['search_btn'])) {
            $search_box = $_POST['search_box'];
            $search_box = filter_var($search_box, FILTER_SANITIZE_STRING);
            $select_movies = $conn->prepare("SELECT * FROM `movies` WHERE name LIKE '%{$search_box}%' OR category LIKE '%{$search_box}%'");
            $select_movies->execute();
            if ($select_movies->rowCount() > 0) {
               while ($fetch_movies = $select_movies->fetch(PDO::FETCH_ASSOC)) {
                  $movie_name_url = urlencode($fetch_movies['name']);
                  ?>
                  <form action="" class="box" method="POST">
                     <img src="uploaded_img/<?= $fetch_movies['image']; ?>" alt="">
                     <div class="name">
                        <a href="movie_recommender.php?movie=<?= $movie_name_url ?>" target="_blank">
                           <?= $fetch_movies['name']; ?>
                        </a>
                     </div>
                     <div class="rating">IMDB: <?= $fetch_movies['rating']; ?>⭐</div>
                     <input type="hidden" name="pid" value="<?= $fetch_movies['id']; ?>">
                     <input type="hidden" name="p_name" value="<?= $fetch_movies['name']; ?>">
                     <input type="hidden" name="p_image" value="<?= $fetch_movies['image']; ?>">
                  </form>
                  <?php
               }
            } else {
               echo '<p class="empty">no result found!</p>';
            }

         }
         ;
         ?>

      </div>

   </section>






   <?php include 'footer.php'; ?>

   <script src="js/script.js"></script>

</body>

</html>