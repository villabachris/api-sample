@extends('layouts.app')
@section('content')
<div class="container-fluid">
    <a class="btn btn-success ml-5 text-light" href="/"> Back </a>
</div>
    @foreach ($search['offers'] as $lender => $detail)
        <div class="card shadow-lg">
            <div class="card-header bg-primary text-light col-md-8 text-center mx-auto">
                <h4>{{$detail['lender']['name']}}</h4>
                <p><span class="text-success badge badge-dark">Lender Code: </span>&nbsp;&nbsp;{{ $detail['lender']['lendercode']}}</p>
            </div>
            <div class="card-body p-0 mt-1">
                <div>
                    <table class="table col-md-8 mx-auto">
                        <thead class="thead-dark">
                            <tr>
                                <th><h4>Details</h4></th>
                                <th><h4>Charges</h4></th>
                            </tr>
                        </thead>
                        <tbody class="bg-light">
                            <td>
                                <p><span class="text-primary">Product Name:</span> {{ $detail['productName'] }}</p>
                                <p><span class="text-primary"> Product Type: </span>{{ $detail['productType'] }}</p>
                                <p><span class="text-primary"> Curency: </span> {{ $detail['currency'] }}</p>
                                <p><span class="text-primary"> Loan Amount: </span>{{ $detail['loanAmount'] }}</p>
                                <p><span class="text-primary"> Interest Rate:</span> {{ $detail['interestRate'] }}</p>
                                <p><span class="text-primary"> Amortization Unit:</span> {{ $detail['amortizationUnit'] }}</p>
                                <p><span class="text-primary"> Loan Proceeds:</span> {{ $detail['loanProceeds'] }}</p>
                                <p><span class="text-primary"> Total Payments:</span> {{ $detail['totalPayments'] }}</p>
                                <p><span class="text-primary"> Loan Duration:</span> {{ $detail['loanDuration'] }}</p>
                                <p><span class="text-primary"> Minimum Duration:</span> {{ $detail['minDuration'] }}</p>
                                <p><span class="text-primary"> Max Duration:</span> {{ $detail['maxDuration'] }}</p>
                            </td>
                            <td>
                                @foreach ($detail['charges'] as $charges => $value)
                                    <p><span class="text-primary">{{$charges}}:</span> {{$value}}</p>
                                @endforeach
                            </td>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    @endforeach
@endsection