<?php

class db
{
    var $con;

    function __construct()
    {
        $this->con = pg_connect("host=localhost port=5432 dbname=sport_ing user=robzeeman password=bonzo");
    }

    function get_items($count)
    {
        $result = pg_query($this->con, "SELECT id, plaats, naam, DATE_PART('year' ,begindatum) as beginjaar, begindatum_soort, DATE_PART('year', einddatum) AS eindjaar, einddatum_soort, levensbeschouwing  FROM vereniging_vereniging LIMIT $count");
        return $this->ass_arr($result);
    }

    function get_sports($id) {
        $result = pg_query($this->con, "SELECT soort_sport AS sport FROM vereniging_sport WHERE vereniging = $id");
        return $this->ass_arr($result);
    }

    function get_province($id) {
        $result = pg_query($this->con, "SELECT provincie FROM vereniging_provincie WHERE vereniging = $id");
        $prov = $this->ass_arr($result);
        if (count($prov)) {
            return $prov[0]["provincie"];
        } else {
            return "";
        }
    }

    function get_landelijk($id) {
        $result = pg_query($this->con, "SELECT naam AS bond FROM landelijke_bond WHERE landelijke_bond = $id");
        return $this->ass_arr($result);
    }

    function get_lokaal($id) {
        $result = pg_query($this->con, "SELECT naam AS bond FROM regionale_bond WHERE regionale_bond = $id");
        return $this->ass_arr($result);
    }

    private
    function ass_arr($results)
    {
        $retArray = array();
        while ($row = pg_fetch_assoc($results)) {
            $retArray[] = $row;
        }
        return $retArray;
    }
}