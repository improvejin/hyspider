CREATE TABLE `movie_db` (
  `id` int(11) unsigned NOT NULL,
  `name` varchar(20) NOT NULL DEFAULT '',
  `actors` varchar(255) NOT NULL DEFAULT '',
  `type` varchar(20) NOT NULL DEFAULT '',
  `score` float NOT NULL DEFAULT '0',
  `duration` varchar(20) NOT NULL DEFAULT '',
  `poster` varchar(255) NOT NULL DEFAULT '',
  `release_date` varchar(20) NOT NULL DEFAULT '',
  `ongoing` bit(1) NOT NULL DEFAULT b'0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `movie_lm` (
  `id` int(11) unsigned NOT NULL,
  `name` varchar(20) NOT NULL DEFAULT '',
  `actors` varchar(255) NOT NULL DEFAULT '',
  `score` float NOT NULL DEFAULT '0',
  `poster` varchar(255) NOT NULL DEFAULT '',
  `release_date` varchar(20) NOT NULL DEFAULT '',
  `ongoing` bit(1) NOT NULL DEFAULT b'0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `movie_mt` (
  `id` int(11) unsigned NOT NULL,
  `name` varchar(20) NOT NULL DEFAULT '',
  `score` float NOT NULL DEFAULT '0',
  `poster` varchar(255) NOT NULL DEFAULT '',
  `version` varchar(10) NOT NULL DEFAULT '',
  `actors` varchar(255) NOT NULL DEFAULT '',
  `release_date` varchar(20) NOT NULL DEFAULT '',
  `ongoing` bit(1) NOT NULL DEFAULT b'0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `movie_tb` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL DEFAULT '',
  `score` float NOT NULL DEFAULT '0',
  `poster` varchar(255) NOT NULL DEFAULT '',
  `actors` varchar(255) NOT NULL DEFAULT '',
  `ongoing` bit(1) NOT NULL DEFAULT b'0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `movie` (
  `id_db` int(11) NOT NULL,
  `id_mt` int(11) NOT NULL DEFAULT '0',
  `id_tb` int(11) NOT NULL DEFAULT '0',
  `id_lm` int(11) NOT NULL DEFAULT '0',
  `name` varchar(20) NOT NULL DEFAULT '',
  `type` varchar(20) NOT NULL DEFAULT '',
  `actors` varchar(255) NOT NULL DEFAULT '',
  `score` float NOT NULL DEFAULT '0',
  `duration` varchar(20) NOT NULL DEFAULT '',
  `poster` varchar(255) NOT NULL DEFAULT '',
  `release_date` varchar(10) NOT NULL DEFAULT '',
  `ongoing` bit(1) NOT NULL DEFAULT b'0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_db`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;