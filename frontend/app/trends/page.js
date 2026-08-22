'use client';

let count = 0;

export default function trends() {

    function increase() {
        console.log('increased');
        count = count + 1;
    }

    return (
    <div>
        <p>{count}</p>
        <button onClick={increase} classname="border-2 border-red-500">Increase</button>
    </div>
    );
}