@extends('layouts.app')
@section('content')
<div class="container">
    <div class="col-md-12 mx-auto card">
        <div class="card-header bg-primary"> 
            <h3 class="card-title text-center text-light">Endpoint</h3>
        </div>
        <div class="card-body">
            <div>
            </div>
            <div>
                <div>
                    <h4>Search Loans:</h4>
                    @if(Session::has('message'))
                <p class="alert {{Session::get('alert-class')}}">{{Session::get('message')}}</p>
                    @endif
                    
                    @if(Session::has('message1'))
                <p class="alert {{Session::get('alert-class')}}">{{Session::get('message1')}}</p>
                    @endif
                    {{-- ///////////////////////// --}}
                            {{-- loan amount --}}
                    {{-- ///////////////////////// --}}
                    <form method="POST" action="/search">
                        @csrf
                        <div class="form-group">
                            <label for="loan">Loan Amount:</label>
                            <select name="loan" id="loan" class="custom-select">
                                <option value =""selected>Choose Amount</option>
                                @for ($i = 10000; $i <= 100000; $i++)
                                    @if ($i % 10000 == 0)
                                        <option value="{{$i}}">{{$i}} Php</option>
                                    @endif
                                @endfor
                            </select>
                        </div>
                        {{-- ///////////////////////// --}}
                            {{-- end of loan amount --}}
                        {{-- ///////////////////////// --}}
                        
                        {{-- ///////////////////////// --}}
                                {{-- duration --}}
                        {{-- ///////////////////////// --}}
                        <div class="form-group">
                            <label for="duration">duration:</label>
                            <select name="duration" id="duration" class="custom-select">
                                <option value ="" selected>Months</option>
                                <option value ="6">6 months </option>
                                @for ($i = 6; $i <= 48; $i++)
                                    @if ($i % 12 == 0)
                                    <option value="{{$i}}">{{$i}} months</option>
                                    @endif
                                    @endfor
                                </select>
                            </div>
                            {{-- ///////////////////////// --}}
                                {{-- end of duration --}}
                            {{-- ///////////////////////// --}}
                
                            
                            {{-- ///////////////////////// --}}
                                {{-- unit & loan type --}}
                            {{-- ///////////////////////// --}}
                            <div class="form-group">
                                <input type="hidden" name="unit" value="MONTHS" class="form-control">
                            </div>
                            <div>
                                <input type="hidden" name="ltype" value="PERSONAL" class="form-control">
                            </div>
                            <button class="btn btn-primary mb-5" type="submit" id="send" > Search </button>
                        </form>
                    </div>    
                </div>              
                {{-- end of unit & loan type --}}

                {{-- ///////////////////////// --}}
                    {{-- lenders table --}}
                {{-- ///////////////////////// --}}
                <div>
                    <table class="table table-striped table-dark">
                        <thead class="">
                            <tr>
                                <th style="width:20px"><h4>Lender Name</h4></th>
                                <th style="width:20px"><h4>Details</h4></th>
                                <th style="width:5px"><h4>Charges</h4></th>
                            </tr>
                        </thead>
                        @foreach($json as $key => $offers)
                        <tbody>
                            @foreach($offers as $val => $name)
                            <tr> 
                                <td>
                                    {{ $name['lender']['name'] }}
                                    <p><span class="text-success">Lender Code: </span>{{ $name['lender']['lendercode']}}</p>
                                </td>
                                <td>
                                    <p><span class="text-primary">Product Name:</span> {{ $name['productName'] }}</p>
                                    <p><span class="text-primary"> Product Type: </span>{{ $name['productType'] }}</p>
                                    <p><span class="text-primary"> Curency: </span> {{ $name['currency'] }}</p>
                                    <p><span class="text-primary"> Loan Amount: </span>{{ $name['loanAmount'] }}</p>
                                    <p><span class="text-primary"> Interest Rate:</span> {{ $name['interestRate'] }}</p>
                                    <p><span class="text-primary"> Amortization Unit:</span> {{ $name['amortizationUnit'] }}</p>
                                    <p><span class="text-primary"> Loan Proceeds:</span> {{ $name['loanProceeds'] }}</p>
                                    <p><span class="text-primary"> Total Payments:</span> {{ $name['totalPayments'] }}</p>
                                    <p><span class="text-primary"> Loan Duration:</span> {{ $name['loanDuration'] }}</p>
                                    <p><span class="text-primary"> Minimum Duration:</span> {{ $name['minDuration'] }}</p>
                                    <p><span class="text-primary"> Max Duration:</span> {{ $name['maxDuration'] }}</p>
                                </td>
                                <td>
                                    @foreach ($name['charges'] as $charges => $value)
                                    <p><span class="text-primary">{{$charges}}:</span> {{$value}}</p>
                                    @endforeach
                                </td>
                            </tr>
                            @endforeach 
                        </tbody>
                        @endforeach
                    </table>
                    {{-- ///////////////////////// --}}
                        {{-- lenders table --}}
                    {{-- ///////////////////////// --}}
                </div>
                <button class="btn btn-success" id="button">click</button>
            </div>  
        </div>
    </div>
    @endsection
    