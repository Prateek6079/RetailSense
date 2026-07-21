import Timeline from "../../components/timeline";
import Graph from "../../components/static_graph";

export default function graph() {
    return (
        <div>
            <Timeline />
            <div className="w-full h-[900px] mt-10 border-2 border-dashed border-gray-400 p-4"> <Graph /> </div>
        </div>
    );
}