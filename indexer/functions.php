<?php

$db = new db();


function formDate($d, $m, $y)
{
    if ($d < 1 || $d > 31) {
        $d = "??";
    } else {
        $d = str_pad($d, 2, "0", STR_PAD_LEFT);
    }
    if ($m < 1 || $m > 12) {
        $m = "??";
    } else {
        $m = str_pad($m, 2, "0", STR_PAD_LEFT);
    }
    if ($y < 500) {
        $y = "????";
    }
    return "$d-$m-$y";
}

function put_mapping()
{
    $mapping = file_get_contents(MAPPING_FILE);
    $ch = curl_init();
    $options = array('Content-type: application/json', 'Content-Length: ' . strlen($mapping));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $options);
    curl_setopt($ch, CURLOPT_URL, MAPPING_URL);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
    curl_setopt($ch, CURLOPT_VERBOSE, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $mapping);
    curl_exec($ch);
    echo "Index mapping sent.\n";
}


function publish($passage, $url)
{
    $json_struc = json_encode($passage);
    $options = array('Content-type: application/json', 'Content-Length: ' . strlen($json_struc));
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $options);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $json_struc);
    //curl_setopt($ch, CURLOPT_VERBOSE, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $response = curl_exec($ch);
    //echo $response;
    curl_close($ch);
}

function indexItems($count)
{
    global $db;
    //put_mapping();
    $items = $db->get_items($count);
    foreach ($items as $item) {
        $item = build_item($item);
        publish($item, INDEX_URL);
        $id = $item["id"];
        echo "$id indexed\n";
        //print_r($item);
    }
}

function build_item($item)
{
    global $db;

    $id = $item["id"];
    $givenname = $item["givenname"];
    $infix = $item["infix"];
    $name = $item["name"];
    if (is_null($infix) || strlen(trim($infix)) == 0) {
        $item["fullname"] = $givenname.' '.$name;
    } else {
        $item["fullname"] = $givenname.' '.$infix.' '.$name;
    }
   
    $item["databases"] =  $db->get_database($id);
    return $item;
}

function getYN($str) {
    if (strlen(trim($str)) > 0) {
        return "yes";
    } else {
        return "no";
    }
}

function getFragment($value) {
    if (strtolower($value) == "fragment") {
        return "yes";
    } else {
        return "no";
    }
}


function simplify_dates($results, $label) {
    $retArray = array();
    foreach ($results as $result) {
        $buffer = array();
        $buffer["date"] = oneCentury($result["date"]);
        $buffer["label"] = $label;
        $tmp = dateRanges($result["numerical_date"]);
        if (count($tmp) == 2) {
            $buffer["lower"] = $tmp["lower"];
            $buffer["upper"] = $tmp["upper"];
        } else {
            $buffer["lower"] = 0;
            $buffer["upper"] = 0;
        }
        $retArray[] = $buffer;
    }
    return $retArray;
}

function dateRanges($date) {
    $parts = explode("-", $date);
    if (count($parts) == 2) {
        if (is_numeric($parts[0]) && is_numeric($parts[1])) {
            return array("lower" => $parts[0], "upper" => $parts[1]);
        } else {
            return array();
        }
    } else {
        return array();
    }
}

function oneCentury($date) {
    $part = substr($date, 0, 4);
    switch($part) {
        case "7th ":
            return " 7th century";
        case "8th ":
            return " 8th century";
        case "9th ":
            return " 9th century";
        case "10th":
            return "10th century";
        case "11th":
            return "11th century";
        default:
            return "Unknown";
    }
}

function is_digitized($id) {
    global $db;

   return $db->getAmountDigitized($id);
}

function is_available($str) {
    if (is_null($str) || $str == "") {
        return "no";
    } else {
        return "yes";
    }
}

function is_image($str) {
    if (is_null($str) || $str == "") {
        return false;
    } else {
        return true;
    }
}

function process_str($str) {
    if ($str == "" || is_null($str)) {
        return "Unknown";
    } else {
        return $str;
    }
}

function get_layout($value) {
    $retValue = "";
    switch($value) {
        case "1":
            $retValue = "one column";
            break;
        case "2":
            $retValue = "two columns";
            break;
        case "3":
            $retValue = "three columns";
            break;
        case "4":
            $retValue = "four columns";
            break;
        default:
            $retValue = "unknown";
            break;
    }
    return $retValue;
}


