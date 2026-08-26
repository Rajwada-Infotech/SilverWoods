-- ============================================================================
-- SilverWoods — Full Blank Database Schema (MySQL)
-- Generated from Django models (core app) + Django built-in auth/admin/sessions
-- Engine: InnoDB, Charset: utf8mb4
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `silverwoods` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `silverwoods`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- Django built-in tables
-- ============================================================================

DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_group_permissions_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- core app tables
-- ============================================================================

DROP TABLE IF EXISTS `core_projectinfo`;
CREATE TABLE `core_projectinfo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `tagline` varchar(500) NOT NULL,
  `description` longtext NOT NULL,
  `address` longtext NOT NULL,
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `pincode` varchar(10) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(254) NOT NULL,
  `website` varchar(200) NOT NULL,
  `map_embed_url` varchar(200) NOT NULL,
  `facebook` varchar(200) NOT NULL,
  `instagram` varchar(200) NOT NULL,
  `twitter` varchar(200) NOT NULL,
  `youtube` varchar(200) NOT NULL,
  `director_name` varchar(200) NOT NULL,
  `director_title` varchar(200) NOT NULL,
  `director_bio` longtext NOT NULL,
  `rera_number` varchar(100) NOT NULL,
  `total_units` int NOT NULL,
  `total_floors` int NOT NULL,
  `total_towers` int NOT NULL,
  `project_area` varchar(100) NOT NULL,
  `possession_date` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_flattype`;
CREATE TABLE `core_flattype` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `bhk` decimal(3,1) NOT NULL,
  `carpet_area` varchar(50) NOT NULL,
  `buildup_area` varchar(50) NOT NULL,
  `terrace_area` varchar(50) NOT NULL,
  `super_buildup_area` varchar(50) NOT NULL,
  `price` decimal(12,2) NOT NULL,
  `price_per_sqft` decimal(10,2) NOT NULL,
  `description` longtext NOT NULL,
  `is_available` tinyint(1) NOT NULL,
  `order` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_amenity`;
CREATE TABLE `core_amenity` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `icon` varchar(50) NOT NULL,
  `description` varchar(300) NOT NULL,
  `order` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_popupad`;
CREATE TABLE `core_popupad` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `description` longtext NOT NULL,
  `flat_type` varchar(50) NOT NULL,
  `link` varchar(200) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_external` tinyint(1) NOT NULL,
  `project_logo` varchar(100) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `order` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_lead`;
CREATE TABLE `core_lead` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `flat_preference` varchar(50) NOT NULL,
  `message` longtext NOT NULL,
  `source` varchar(50) NOT NULL,
  `popup_ad_id` bigint DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_contacted` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_lead_popup_ad_id_d4b359e1_fk_core_popupad_id` (`popup_ad_id`),
  CONSTRAINT `core_lead_popup_ad_id_d4b359e1_fk_core_popupad_id` FOREIGN KEY (`popup_ad_id`) REFERENCES `core_popupad` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_sitevisitor`;
CREATE TABLE `core_sitevisitor` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `ip_address` char(39) NOT NULL,
  `user_agent` longtext NOT NULL,
  `page_visited` varchar(500) NOT NULL,
  `visited_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_review`;
CREATE TABLE `core_review` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `rating` int NOT NULL,
  `comment` longtext NOT NULL,
  `designation` varchar(100) NOT NULL,
  `is_approved` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_buildingflat`;
CREATE TABLE `core_buildingflat` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tower` varchar(10) NOT NULL,
  `floor` int NOT NULL,
  `flat_number` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL,
  `flat_type_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_buildingflat_tower_flat_number_df58674f_uniq` (`tower`,`flat_number`),
  KEY `core_buildingflat_flat_type_id_7ced0578_fk_core_flattype_id` (`flat_type_id`),
  CONSTRAINT `core_buildingflat_flat_type_id_7ced0578_fk_core_flattype_id` FOREIGN KEY (`flat_type_id`) REFERENCES `core_flattype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_villaplot`;
CREATE TABLE `core_villaplot` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `villa_no` int NOT NULL,
  `status` varchar(20) NOT NULL,
  `owner_name` varchar(200) NOT NULL,
  `sold_at` datetime(6) DEFAULT NULL,
  `notes` longtext NOT NULL,
  `reserved_by` varchar(200) NOT NULL,
  `reserved_until` datetime(6) DEFAULT NULL,
  `completion_pct` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `villa_no` (`villa_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_brochureimage`;
CREATE TABLE `core_brochureimage` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `image` varchar(100) NOT NULL,
  `order` int NOT NULL,
  `caption` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `core_chatbotqa`;
CREATE TABLE `core_chatbotqa` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `question` varchar(500) NOT NULL,
  `answer` longtext NOT NULL,
  `keywords` varchar(500) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `order` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- End of schema — all tables blank (no rows). 21 tables total:
-- 11 Django built-in (auth/admin/content-type/session/migrations)
-- 10 core app tables
-- ============================================================================
