<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Input;
use Illuminate\Http\Request;
use Illuminate\Support\Arr;
use GuzzleHttp\Client;

class HomeController extends Controller
{
    public function home(){
       $client = new Client();
       $request = $client->get('http://lender-mgr-staging.ayannah.com/loanamount/100000/duration/12/unit/MONTHS/loanType/PERSONAL/');
       $response = $request->getBody()->getContents();
    //    dd(gettype($response));
       $json = json_decode($response,true);
    //    dd(gettype($json));
    //    $data = Arr::collapse($json);
    //    ($data));
       return view('home', ['json'=>$json]);
    }

    public function about(){
        return view('about');
    }

}
