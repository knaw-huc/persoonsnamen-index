<?php

class db
{
    var $con;

    function __construct()
    {
        $this->con = pg_connect("host=localhost port=5432 dbname=persoonsnamenindex user=robzeeman password=bonzo");
    }

    function get_items($count)
    {
        $result = pg_query($this->con, "SELECT _id, name, infix, givenname, life_hint_begin, life_hint_end  FROM persons LIMIT $count");
        return $this->ass_arr($result);
    }

    function get_databse($id) {
        $result = pg_query($this->con, "SELECT _id,name FROM database);
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
