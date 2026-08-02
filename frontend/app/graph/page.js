import Timeline from "../../components/timeline";
import Graph from "../../components/static_graph";
import Card from "../../components/card";
import BarChart from "../../components/barChart";
import PieChart from "../../components/pieChart";
import List from "../../components/list";
import { Activity, CircleCheckBig, Stethoscope } from "lucide-react";

const card1 = {
    icon: <Activity size={35} strokeWidth={2}/>,
    title: "Business Health",
    content: <BarChart />,
    description: "View the probability graph of the model's predictions.",
};

const card2 = {
    icon: <CircleCheckBig size={35} strokeWidth={2}/>,
    title: "Observed Evidence",
    content: <List />,
    description: "View the probability graph of the model's predictions.",
};

const card3 = {
    icon: <Stethoscope size={35} strokeWidth={2}/>,
    title: "Likely Causes",
    content: <PieChart />,
    description: "View the probability graph of the model's predictions.",
};

export default function graph() {
    return (
        <div>
            <Timeline />
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-10">
                <Card icon={card1.icon} content={card1.content} title={card1.title} description={card1.description} />
                <Card icon={card2.icon} content={card2.content} title={card2.title} description={card2.description} />
                <Card icon={card3.icon} content={card3.content} title={card3.title} description={card3.description} />
            </div>
            <div className="w-full h-[900px] mt-10 border-2 border-dashed border-gray-400 p-4"> <Graph /> </div>
        </div>
    );
}