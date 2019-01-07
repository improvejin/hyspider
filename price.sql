CREATE TABLE `price_lm` (
  `cinema_id` int(11) unsigned NOT NULL,
  `movie_id` int(11) unsigned NOT NULL,
  `show_date` date NOT NULL,
  `begin` varchar(10) NOT NULL,
  `end` varchar(10) NOT NULL DEFAULT '',
  `language` varchar(20) NOT NULL DEFAULT '',
  `hall` varchar(30) NOT NULL DEFAULT '',
  `price` float NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cinema_id`,`movie_id`,`show_date`,`begin`),
  KEY `idx_cinema_id` (`cinema_id`) USING BTREE,
  KEY `idx_movie_id` (`movie_id`) USING BTREE,
  KEY `idx_show_date` (`show_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `price_mt` (
  `cinema_id` int(11) unsigned NOT NULL,
  `movie_id` int(11) unsigned NOT NULL,
  `show_date` date NOT NULL,
  `begin` varchar(10) NOT NULL,
  `end` varchar(10) NOT NULL DEFAULT '',
  `language` varchar(20) NOT NULL DEFAULT '',
  `hall` varchar(30) NOT NULL DEFAULT '',
  `price` float NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cinema_id`,`movie_id`,`show_date`,`begin`),
  KEY `idx_cinema_id` (`cinema_id`) USING BTREE,
  KEY `idx_movie_id` (`movie_id`) USING BTREE,
  KEY `idx_show_date` (`show_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `price_tb` (
  `cinema_id` int(11) NOT NULL,
  `movie_id` int(11) NOT NULL,
  `show_date` date NOT NULL,
  `begin` varchar(10) NOT NULL,
  `end` varchar(10) NOT NULL DEFAULT '',
  `language` varchar(20) NOT NULL DEFAULT '',
  `hall` varchar(30) NOT NULL DEFAULT '',
  `price` float NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cinema_id`,`movie_id`,`show_date`,`begin`),
  KEY `idx_cinema_id` (`cinema_id`) USING BTREE,
  KEY `idx_movie_id` (`movie_id`) USING BTREE,
  KEY `idx_show_date` (`show_date`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `price` (
  `cinema_id` int(11) NOT NULL,
  `movie_id` int(11) NOT NULL,
  `show_date` date NOT NULL,
  `begin` varchar(10) NOT NULL,
  `end` varchar(10) NOT NULL DEFAULT '',
  `language` varchar(20) NOT NULL DEFAULT '',
  `hall` varchar(30) NOT NULL DEFAULT '',
  `price_mt` float NOT NULL DEFAULT '0',
  `price_tb` float NOT NULL DEFAULT '0',
  `price_lm` float NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`cinema_id`,`movie_id`,`show_date`,`begin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;