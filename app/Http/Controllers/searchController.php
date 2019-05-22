<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Input;
use Illuminate\Support\Arr;
use Illuminate\Http\Request;
use GuzzleHttp\Client;
use Session;

class searchController extends Controller
{
    public function search(){
        
        $loan = Input::get('loan');
        $duration = Input::get('duration');

        if(!$loan || !$duration){
            Session::flash('message', 'Please fill the field');
            Session::flash('alert-class', 'alert-danger');
            return redirect('/');
        }else{
            $client = new Client();
            $request = $client->get("http://lender-mgr-staging.ayannah.com/loanamount/$loan/duration/$duration/unit/MONTHS/loanType/PERSONAL/");
            $response = $request->getBody()->getContents();
            
            $search = json_decode($response,true);
            // dd($search['offers']);
            if($search['offers'] == []){
                Session::flash('message1', 'Sorry, there is no available loan amount that you choose');
                Session::flash('alert-class', 'alert-danger');
                return redirect('/');
            }
            return view('/search', ['search'=>$search]);
        }
    }
}
