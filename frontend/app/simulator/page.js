"use client";

import { useEffect, useState } from "react";
import BouncyList from '../../components/bouncyList';
import InputBox from '../../components/inputBox';

export default function analysis() {
    const [simulationName, setSimulationName] = useState("");
    const [simulations, setSimulations] = useState([]);

    useEffect(() => {
        const loadSimulations = async () => {
            const response = await fetch("/api/simulations");

            if (response.ok) {
                setSimulations(await response.json());
            }
        };

        loadSimulations();
    }, []);

    const createSimulation = async () => {
        const name = simulationName.trim();

        if (!name) return;

        const response = await fetch("/api/simulations", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name }),
        });

        if (!response.ok) return;

        const simulation = await response.json();
        setSimulations((current) => [...current, simulation]);
        setSimulationName("");
    };

    return (
    <div>
    <h1 className="mb-3 text-center text-2xl font-light tracking-[0.2em] text-zinc-200">Simulations</h1>
    <div className="mx-auto mb-8 h-px w-24 bg-gradient-to-r from-transparent via-zinc-500 to-transparent" />
    <div className="flex items-center gap-3">
        <InputBox id="demo-input"
                label="Create New Simulation"
                type="text"
                value={simulationName}
                onChange={(event) => setSimulationName(event.target.value)}
                onKeyDown={(event) => {
                    if (event.key === "Enter") createSimulation();
                }} />
        <button
            type="button"
            aria-label="Create simulation"
            title="Create simulation"
            onClick={createSimulation}
            className="group inline-flex size-11 shrink-0 items-center justify-center rounded-md border-2 border-white bg-black text-white shadow-[3px_3px_0_0_white] transition-all hover:translate-x-px hover:translate-y-px hover:bg-white hover:text-black hover:shadow-[1px_1px_0_0_white] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white active:translate-x-[3px] active:translate-y-[3px] active:shadow-none"
        >
            <svg
                aria-hidden="true"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                className="size-5 transition-transform group-hover:rotate-90"
            >
                <path d="M12 5v14M5 12h14" />
            </svg>
        </button>
    </div>
    <div className="w-full">
        <BouncyList items={simulations} />
    </div>
    </div>
    );
}
