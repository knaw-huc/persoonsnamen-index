<?php
error_reporting(E_ALL);
include('db.class.php');
include('functions.php');

define('ITEMS', 30000);
define("MAPPING_URL", "http://localhost:9200/pni");
define('INDEX_URL', 'http://localhost:9200/pni/_doc');

indexItems(ITEMS);