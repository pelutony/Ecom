/* swiper js */
let swipers = new Swiper(".banner", {
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
      },
  });

/*swiper jumbo*/
let swiper = new Swiper(".jumboSwipe", {
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
      },
    slidesPerView: 4,
    spaceBetween:-20,
  });