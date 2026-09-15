# [1.2.0](https://github.com/BastianBN/meal_management/compare/v1.1.0...v1.2.0) (2026-09-15)


### Features

* **ui:** add booking count and participant list to results and normalize copy ([d201d81](https://github.com/BastianBN/meal_management/commit/d201d81ab413254fd9e09930b839af75c5505014))

# [1.1.0](https://github.com/BastianBN/meal_management/compare/v1.0.0...v1.1.0) (2026-09-15)


### Features

* **ui:** implement grand french bistro themes (la carte and ardoise) with open book layout and brass details ([c299d58](https://github.com/BastianBN/meal_management/commit/c299d581fd1bc4906cc9b9edb48fe4d15b6cc54e))

# 1.0.0 (2026-09-15)


### Bug Fixes

* **backend:** add resilient multi-provider geocoder and fail cleanly on homepage when restaurant search fails ([23e1067](https://github.com/BastianBN/meal_management/commit/23e10671929eaa1ba5872938457d9fe4907fbf40))
* **ci:** resolve setuptools package discovery error and use uv sync in workflows ([727532a](https://github.com/BastianBN/meal_management/commit/727532a96c10935b4e18f8437dc69e6a04386af7))
* place ranking and leaderboard prominently at the top of results view ([e68086d](https://github.com/BastianBN/meal_management/commit/e68086d0664f80be7cf96268778bd9ad14afc350))
* **places:** race high-availability Overpass mirrors concurrently and add Nominatim amenity fallback ([035da4a](https://github.com/BastianBN/meal_management/commit/035da4a3e757eae6ae7106f7755ce31f07bcfc89)), closes [hi#availability](https://github.com/hi/issues/availability)
* **scripts:** use uv run python for dev and start scripts ([2dc764e](https://github.com/BastianBN/meal_management/commit/2dc764ea0a6415020e154328b3ad7887f8db7742))


### Features

* add interactive OpenStreetMap with pins, fix validation button styling, and improve menu parsing with Google card links ([f87772b](https://github.com/BastianBN/meal_management/commit/f87772bfe4038bd99520018ab83ed37d1610dfd9))
* **frontend:** replace walking distance buttons with slider and dynamic duration presets ([d811148](https://github.com/BastianBN/meal_management/commit/d8111489c636cecce254723e8a9ef6acaa56b82b))
* increase walking speed to 6 km/h and expand slider range up to 35 min (3.5 km) ([ff4677e](https://github.com/BastianBN/meal_management/commit/ff4677e34479cb75395a71ed87111e4bc7b5cecd))
* initial release of meal manager platform with live voting, osm discovery, and menu scraper ([3a42b75](https://github.com/BastianBN/meal_management/commit/3a42b75a068a8a36d97da6ed533c380c111a1695))
* **places:** increase restaurant limit up to 50, add rating scoring and stratified distance distribution ([29ec2f8](https://github.com/BastianBN/meal_management/commit/29ec2f8e76dbcd889d4d01ca138ce51086e95acb))
* **ui:** implement minimalist french bistro and bouchon lyonnais slate design with cormorant garamond typography ([350dcff](https://github.com/BastianBN/meal_management/commit/350dcffdaa3b17ae92b927dc87f248533683bb6a))
* **ui:** redesign frontend with bistrot aesthetic and fix card button overflow ([4e74187](https://github.com/BastianBN/meal_management/commit/4e74187434b12f8e50118608c05877b0333d0e5a))
* **ui:** redesign frontend with wabi-sabi aesthetic, washi paper texture, and shippori mincho typography ([06e1232](https://github.com/BastianBN/meal_management/commit/06e12320993f22e218db18a433c1938ff584a370))
* **ui:** warm amber-terracotta washi background and full-page coverage ([74ae6f5](https://github.com/BastianBN/meal_management/commit/74ae6f51250406c239dc30485040363d0d457a94))
