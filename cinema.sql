CREATE TABLE `cinema_lm` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL DEFAULT '',
  `city` varchar(20) NOT NULL DEFAULT '',
  `district` varchar(20) NOT NULL DEFAULT '',
  `addr` varchar(100) NOT NULL DEFAULT '',
  `phone` varchar(30) NOT NULL DEFAULT '',
  `lat_lng` varchar(50) NOT NULL DEFAULT '',
  `location` point NOT NULL,
  `precise` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `confidence` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `min_price` float NOT NULL DEFAULT '0',
  `price_update_time` datetime NOT NULL DEFAULT '2018-08-25 00:00:00',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_city` (`city`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cinema_tb` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL DEFAULT '',
  `city` varchar(20) NOT NULL DEFAULT '',
  `district` varchar(20) NOT NULL DEFAULT '',
  `addr` varchar(100) NOT NULL DEFAULT '',
  `phone` varchar(30) NOT NULL DEFAULT '',
  `lat_lng` varchar(50) NOT NULL DEFAULT '',
  `location` point NOT NULL,
  `precise` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `confidence` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `min_price` float NOT NULL DEFAULT '0',
  `price_update_time` datetime NOT NULL DEFAULT '2018-08-25 00:00:00',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_city` (`city`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cinema_mt` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL DEFAULT '',
  `city` varchar(20) NOT NULL DEFAULT '',
  `district` varchar(20) NOT NULL DEFAULT '',
  `addr` varchar(100) NOT NULL DEFAULT '',
  `phone` varchar(30) NOT NULL DEFAULT '',
  `lat_lng` varchar(50) NOT NULL DEFAULT '',
  `location` point NOT NULL,
  `precise` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `confidence` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `min_price` float NOT NULL DEFAULT '0',
  `price_update_time` datetime NOT NULL DEFAULT '2018-08-25 00:00:00',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_city` (`city`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `cinema` (
  `id_mt` int(11) NOT NULL,
  `id_tb` int(255) NOT NULL DEFAULT '0',
  `id_lm` int(255) NOT NULL DEFAULT '0',
  `name` varchar(30) NOT NULL DEFAULT '',
  `city` varchar(20) NOT NULL DEFAULT '',
  `district` varchar(20) NOT NULL DEFAULT '',
  `addr` varchar(100) NOT NULL DEFAULT '',
  `lat_lng` varchar(50) NOT NULL DEFAULT '',
  `location` point DEFAULT NULL,
  `min_price` float NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_mt`),
  KEY `idx_id_tb` (`id_tb`) USING BTREE,
  KEY `idx_id_lm` (`id_lm`) USING BTREE,
  KEY `idx_city` (`city`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- mysql8提供窗口函数可计算new_rank, new_rank防止一个id_mt匹配了多个id_matched, 保证cinema中id_mt唯一
replace INTO cinema (id_mt, id_lm, id_tb)
SELECT *
FROM (
	SELECT COALESCE(t1.id_mt, t2.id_mt) AS id_mt, COALESCE(id_lm, 0), COALESCE(id_tb, 0)
	FROM (
		SELECT *
		FROM (
			SELECT id_mt, id_matched AS id_lm
				, IF(@tmp = id_mt, @rank := @rank + 1, @rank := 1) AS new_rank
				, @tmp := id_mt AS tmp
			FROM match_cinema_lm2mt
			WHERE is_delete = 0
			ORDER BY id_mt
		) t
		WHERE new_rank = 1
	) t1
		LEFT JOIN (
			SELECT *
			FROM (
				SELECT id_mt, id_matched AS id_tb
					, IF(@tmp = id_mt, @rank := @rank + 1, @rank := 1) AS new_rank
					, @tmp := id_mt AS tmp
				FROM match_cinema_tb2mt
				WHERE is_delete = 0
				ORDER BY id_mt
			) t
			WHERE new_rank = 1
		) t2
		ON t1.id_mt = t2.id_mt
	UNION
	SELECT COALESCE(t1.id_mt, t2.id_mt) AS id_mt, COALESCE(id_lm, 0), COALESCE(id_tb, 0)
	FROM (
		SELECT *
		FROM (
			SELECT id_mt, id_matched AS id_lm
				, IF(@tmp = id_mt, @rank := @rank + 1, @rank := 1) AS new_rank
				, @tmp := id_mt AS tmp
			FROM match_cinema_lm2mt
			WHERE is_delete = 0
			ORDER BY id_mt
		) t
		WHERE new_rank = 1
	) t1
		RIGHT JOIN (
			SELECT *
			FROM (
				SELECT id_mt, id_matched AS id_tb
					, IF(@tmp = id_mt, @rank := @rank + 1, @rank := 1) AS new_rank
					, @tmp := id_mt AS tmp
				FROM match_cinema_tb2mt
				WHERE is_delete = 0
				ORDER BY id_mt
			) t
			WHERE new_rank = 1
		) t2
		ON t1.id_mt = t2.id_mt
) t;

-- 根据cinema_mt更新cinema其他字段
update cinema join cinema_mt on (cinema.id_mt = cinema_mt.id and cinema.name='')
set cinema.name = cinema_mt.name, cinema.city = cinema_mt.city, cinema.district = cinema_mt.district, cinema.addr = cinema_mt.addr,
cinema.location = cinema_mt.location,cinema.lat_lng=cinema_mt.lat_lng;


-- price 综合多个渠道取最低者
update cinema join cinema_mt on (cinema.id_mt = cinema_mt.id) join cinema_lm on (cinema.id_lm = cinema_lm.id) join cinema_tb on (cinema.id_tb = cinema_tb.id)
set cinema.price = LEAST(ifnull(cinema_mt.price,88), ifnull(cinema_lm.price,88), ifnull(cinema_tb.price,88))

-- 按距离由近到远
select st_distance( Point(31.1604447050825,121.357030810457), location) , id_mt, name, addr   from cinema  order by st_distance( Point(31.1604447050825, 121.357030810457), location) asc