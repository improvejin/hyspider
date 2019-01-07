CREATE TABLE `match_movie_tb2db` (
  `id_db` int(11) NOT NULL,
  `id_matched` int(11) NOT NULL,
  `match_type` tinyint(1) DEFAULT NULL,
  `match_score` float DEFAULT NULL,
  `match_step` tinyint(1) DEFAULT NULL,
  `is_delete` tinyint(1) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_db`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `match_movie_mt2db` (
  `id_db` int(11) NOT NULL,
  `id_matched` int(11) NOT NULL,
  `match_type` tinyint(1) DEFAULT NULL,
  `match_score` float DEFAULT NULL,
  `match_step` tinyint(1) DEFAULT NULL,
  `is_delete` tinyint(1) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_db`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `match_movie_lm2db` (
  `id_db` int(11) NOT NULL,
  `id_matched` int(11) NOT NULL,
  `match_type` tinyint(1) DEFAULT NULL,
  `match_score` float DEFAULT NULL,
  `match_step` tinyint(1) DEFAULT NULL,
  `is_delete` tinyint(1) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_db`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;