CREATE TABLE `announcements` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`category` text NOT NULL,
	`summary` text NOT NULL,
	`published_at` integer NOT NULL,
	`member_only` integer DEFAULT false NOT NULL
);
--> statement-breakpoint
CREATE TABLE `events` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`event_date` integer NOT NULL,
	`location` text NOT NULL,
	`summary` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `member_applications` (
	`id` text PRIMARY KEY NOT NULL,
	`company_name` text NOT NULL,
	`contact_name` text NOT NULL,
	`position` text NOT NULL,
	`phone` text NOT NULL,
	`email` text NOT NULL,
	`location` text NOT NULL,
	`interest_area` text NOT NULL,
	`purpose` text NOT NULL,
	`status` text DEFAULT '대기' NOT NULL,
	`reviewer_email` text,
	`created_at` integer NOT NULL,
	`reviewed_at` integer
);
--> statement-breakpoint
CREATE TABLE `member_companies` (
	`id` text PRIMARY KEY NOT NULL,
	`category` text NOT NULL,
	`company_name` text NOT NULL,
	`representative` text NOT NULL,
	`role` text NOT NULL,
	`location` text NOT NULL,
	`note` text,
	`contact_email` text,
	`approved_at` integer
);
--> statement-breakpoint
CREATE TABLE `resources` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`category` text NOT NULL,
	`file_name` text NOT NULL,
	`summary` text NOT NULL,
	`member_only` integer DEFAULT true NOT NULL,
	`published_at` integer NOT NULL
);
