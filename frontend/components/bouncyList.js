"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  ChartNoAxesCombined,
  ChevronDown,
  Play,
  Settings2,
  Trash2,
  X,
} from "lucide-react";
import {
  useCallback,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  useEffect,
} from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import SimulationResults from "./simulationResults";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export const EASE_OUT = [0.16, 1, 0.3, 1];
export const EASE_IN_OUT = [0.77, 0, 0.175, 1];
export const EASE_DRAWER = [0.32, 0.72, 0, 1];

export const EASE_OUT_CSS = "cubic-bezier(0.16, 1, 0.3, 1)";

export const SPRING_PRESS = {
  type: "spring",
  stiffness: 500,
  damping: 30,
  mass: 0.6,
};

export const SPRING_SWAP = {
  type: "spring",
  stiffness: 460,
  damping: 30,
  mass: 0.55,
};

export const SPRING_PANEL = {
  type: "spring",
  stiffness: 420,
  damping: 40,
  mass: 0.5,
};

export const SPRING_LAYOUT = {
  type: "spring",
  stiffness: 360,
  damping: 32,
  mass: 0.6,
};

export const SPRING_MOUSE = {
  stiffness: 200,
  damping: 15,
  mass: 0.3,
};

const ROW_TRANSITION = {
  type: "spring",
  duration: 0.55,
  bounce: 0.38,
};

const CONTENT_OPEN_TRANSITION = {
  type: "spring",
  duration: 0.58,
  bounce: 0.32,
};

const CONTENT_CLOSE_TRANSITION = {
  type: "spring",
  duration: 0.46,
  bounce: 0.26,
};

const DESCRIPTION_TRANSITION = {
  duration: 0.18,
  ease: EASE_OUT,
};

const CHEVRON_TRANSITION = {
  type: "spring",
  duration: 0.42,
  bounce: 0.28,
};

function useControllableAccordionValue({
  value,
  defaultValue,
  onValueChange,
}) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? null);
  const isControlled = value !== undefined;
  const currentValue = value ?? internalValue;

  const setValue = useCallback(
    (next) => {
      if (!isControlled) {
        setInternalValue(next);
      }

      onValueChange?.(next);
    },
    [isControlled, onValueChange],
  );

  return [currentValue, setValue];
}

function BouncyAccordionRow({
  item,
  open,
  startsGroup,
  endsGroup,
  separatedFromPrevious,
  contentId,
  triggerId,
  reduce,
  classNames,
  onToggle,
  onConfigure,
  onDelete,
  onRunSimulation,
  isRunning,
  simulationResult,
}) {
  const contentRef = useRef(null);
  const [contentHeight, setContentHeight] = useState(0);

  useLayoutEffect(() => {
    const node = contentRef.current;
    if (!node) return;

    const updateHeight = () => {
      setContentHeight(node.offsetHeight);
    };

    updateHeight();

    const observer = new ResizeObserver(updateHeight);
    observer.observe(node);

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <motion.div
      initial={false}
      animate={{ marginTop: separatedFromPrevious ? 12 : 0 }}
      transition={reduce ? { duration: 0 } : ROW_TRANSITION}
    >
      <motion.div
        data-state={open ? "open" : "closed"}
        initial={false}
        animate={{
          borderTopLeftRadius: startsGroup ? 28 : 0,
          borderTopRightRadius: startsGroup ? 28 : 0,
          borderBottomLeftRadius: endsGroup ? 28 : 0,
          borderBottomRightRadius: endsGroup ? 28 : 0,
        }}
        transition={reduce ? { duration: 0 } : ROW_TRANSITION}
        className={cn(
          "overflow-hidden bg-card text-card-foreground",
          item.disabled && "opacity-50",
          classNames?.item,
        )}
      >
        <div className="flex items-center">
          <button
            id={triggerId}
            type="button"
            disabled={item.disabled}
            aria-expanded={open}
            aria-controls={contentId}
            onClick={onToggle}
            className={cn(
              "flex min-h-[54px] min-w-0 flex-1 items-center gap-4 px-5 text-left outline-none transition-colors",
              "focus-visible:bg-muted/25",
              "disabled:pointer-events-none",
              classNames?.trigger,
            )}
          >
            <span
              className={cn(
                "grid h-7 w-7 shrink-0 place-items-center text-muted-foreground",
                classNames?.icon,
              )}
            >
              {item.icon ?? <ChartNoAxesCombined className="h-4 w-4" />}
            </span>

            <span
              className={cn(
                "min-w-0 flex-1 truncate text-[15px] font-medium text-foreground",
                classNames?.title,
              )}
            >
              {item.title}
            </span>

            <motion.span
              aria-hidden
              animate={{ rotate: open ? 180 : 0 }}
              transition={reduce ? { duration: 0 } : CHEVRON_TRANSITION}
              className={cn(
                "grid h-6 w-6 shrink-0 place-items-center text-muted-foreground",
                classNames?.chevron,
              )}
            >
              <ChevronDown className="h-4 w-4" />
            </motion.span>
          </button>

          <button
            type="button"
            aria-label={`Configure ${item.title}`}
            title={`Configure ${item.title}`}
            onClick={onConfigure}
            className="mr-1 grid h-8 w-8 shrink-0 place-items-center rounded-md text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:pointer-events-none"
          >
            <Settings2 aria-hidden="true" className="h-4 w-4" />
          </button>

          <button
            type="button"
            aria-label={`Delete ${item.title}`}
            title={`Delete ${item.title}`}
            onClick={onDelete}
            className="mr-4 grid h-8 w-8 shrink-0 place-items-center rounded-md text-muted-foreground transition-colors hover:bg-destructive/15 hover:text-destructive focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-destructive disabled:pointer-events-none"
          >
            <Trash2 aria-hidden="true" className="h-4 w-4" />
          </button>
        </div>
        
        <motion.div
          id={contentId}
          role="region"
          aria-labelledby={triggerId}
          aria-hidden={!open}
          initial={false}
          animate={{
            height: open && item.description ? contentHeight : 0,
          }}
          transition={
            reduce
              ? { duration: 0 }
              : open
                ? CONTENT_OPEN_TRANSITION
                : CONTENT_CLOSE_TRANSITION
          }
          className={cn("overflow-hidden", classNames?.content)}
        >
          <motion.div
            ref={contentRef}
            animate={{
              opacity: open ? 1 : 0,
            }}
            transition={reduce ? { duration: 0 } : DESCRIPTION_TRANSITION}
            className="px-5 pb-5"
          >
            <div
              className={cn(
                "flex items-center justify-between gap-4 text-[15px] leading-6 text-muted-foreground",
                classNames?.description,
              )}
            >
              <span>
                {item.configuration === null
                  ? "Configure simulation parameters to run the simulation."
                  : item.description}
              </span>
              {item.configuration !== null && (
                <button
                  type="button"
                  onClick={onRunSimulation}
                  disabled={isRunning}
                  className="inline-flex shrink-0 items-center gap-2 rounded-md border-2 border-white bg-black px-3 py-2 text-sm font-semibold text-white shadow-[3px_3px_0_0_white] transition-all hover:translate-x-px hover:translate-y-px hover:bg-white hover:text-black hover:shadow-[1px_1px_0_0_white] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white active:translate-x-[3px] active:translate-y-[3px] active:shadow-none disabled:cursor-wait disabled:opacity-60"
                >
                  <Play aria-hidden="true" className="h-3.5 w-3.5" />
                  {isRunning ? "Running..." : "Run simulation"}
                </button>
              )}
            </div>
            <SimulationResults result={simulationResult} />
          </motion.div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}

export function BouncyAccordion({
  items,
  defaultValue = null,
  collapsible = true,
  className,
  classNames,
}) {
  const reduce = useReducedMotion();
  const baseId = useId();
  const [visibleItems, setVisibleItems] = useState(items);
  const [activeValues, setActiveValues] = useState(defaultValue ? [defaultValue] : []);
  const [configuredItem, setConfiguredItem] = useState(null);
  const [configurationName, setConfigurationName] = useState("");
  const [configurationVariables, setConfigurationVariables] = useState([]);
  const [configuration, setConfiguration] = useState({});
  const [runningSimulationId, setRunningSimulationId] = useState(null);
  const [simulationResults, setSimulationResults] = useState(() =>
    Object.fromEntries(
      items
        .filter((item) => item.result)
        .map((item) => [
          item.id,
          {
            simulationId: item.id,
            configuration: item.configuration,
            variables: item.result,
            score: item.score,
          },
        ]),
    ),
  );
  const deletedItemIds = useRef(new Set());

  useEffect(() => {
    const incomingIds = new Set(items.map((item) => item.id));

    deletedItemIds.current.forEach((id) => {
      if (!incomingIds.has(id)) {
        deletedItemIds.current.delete(id);
      }
    });

    setVisibleItems(
      items.filter((item) => !deletedItemIds.current.has(item.id)),
    );
    setSimulationResults((current) => ({
      ...current,
      ...Object.fromEntries(
        items
          .filter((item) => item.result)
          .map((item) => [
            item.id,
            {
              simulationId: item.id,
              configuration: item.configuration,
              variables: item.result,
              score: item.score,
            },
          ]),
      ),
    }));
  }, [items]);

  useEffect(() => {
    const loadConfiguration = async () => {
      const response = await fetch("/api/simulation-configuration");

      if (!response.ok) return;

      const data = await response.json();
      setConfigurationVariables(data.variables ?? []);
    };

    loadConfiguration();
  }, []);

  const toggleItem = useCallback(
    (id) => {
      setActiveValues((prev) => {
        if (prev.includes(id)) {
          return collapsible ? prev.filter((item) => item !== id) : prev;
        }

        return [...prev, id];
      });
    },
    [collapsible],
  );

  const deleteItem = useCallback(async (id) => {
    const response = await fetch(
      `/api/simulations?id=${encodeURIComponent(id)}`,
      { method: "DELETE" },
    );

    if (!response.ok) return;

    deletedItemIds.current.add(id);
    setVisibleItems((current) => current.filter((item) => item.id !== id));
    setActiveValues((current) => current.filter((value) => value !== id));
  }, []);

  const configureItem = useCallback((item) => {
    if (!configurationVariables.length) return;

    setConfiguredItem(item);
    setConfigurationName(item.title);
    setConfiguration(
      Object.fromEntries(
        configurationVariables.map((variable) => [
          variable.name,
          item.configuration?.[variable.name] ?? variable.labels[0] ?? "",
        ]),
      ),
    );
  }, [configurationVariables]);

  const saveConfiguration = useCallback(async (event) => {
    event.preventDefault();

    if (!configuredItem) return;

    const response = await fetch("/api/simulations", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: configuredItem.id,
        name: configurationName,
        configuration,
        result: null,
        score: null,
      }),
    });

    if (!response.ok) return;

    const updatedSimulation = await response.json();
    setVisibleItems((current) =>
      current.map((item) =>
        item.id === updatedSimulation.id ? updatedSimulation : item,
      ),
    );
    setSimulationResults((current) => {
      const next = { ...current };
      delete next[updatedSimulation.id];
      return next;
    });
    setConfiguredItem(null);
  }, [configuration, configurationName, configuredItem]);

  const runSimulation = useCallback(async (item) => {
    if (item.configuration === null || runningSimulationId) return;

    setRunningSimulationId(item.id);

    const result = await new Promise((resolve) => {
      setTimeout(() => {
        const variables = Object.fromEntries(
          configurationVariables.map((variable) => {
            const weights = variable.labels.map(() => Math.random());
            const total = weights.reduce((sum, weight) => sum + weight, 0);

            return [
              variable.name,
              Object.fromEntries(
                variable.labels.map((label, index) => [
                  label,
                  Number((weights[index] / total).toFixed(3)),
                ]),
              ),
            ];
          }),
        );

        resolve({
          simulationId: item.id,
          configuration: item.configuration,
          variables,
          score: configurationVariables.length
            ? configurationVariables.reduce(
                (sum, variable) =>
                  sum + (variables[variable.name]?.[item.configuration[variable.name]] || 0),
                0,
              ) / configurationVariables.length
            : 0,
        });
      }, 500);
    });

    await fetch("/api/simulations", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: item.id,
        configuration: item.configuration,
        result: result.variables,
        score: result.score,
      }),
    });

    setSimulationResults((current) => ({ ...current, [item.id]: result }));
    setRunningSimulationId(null);
    return result;
  }, [configurationVariables, runningSimulationId]);

  return (
    <div className={cn("w-full", className, classNames?.root)}>
      {visibleItems.map((item, index) => {
        const open = activeValues.includes(item.id);
        const previousIsOpen =
          index > 0 && activeValues.includes(visibleItems[index - 1].id);
        const nextIsOpen =
          index < visibleItems.length - 1 &&
          activeValues.includes(visibleItems[index + 1].id);
        const startsGroup = open || index === 0 || previousIsOpen;
        const endsGroup = open || index === visibleItems.length - 1 || nextIsOpen;
        const separatedFromPrevious = index > 0 && (open || previousIsOpen);
        const contentId = `${baseId}-${item.id}-content`;
        const triggerId = `${baseId}-${item.id}-trigger`;

        return (
          <BouncyAccordionRow
            key={item.id}
            item={item}
            open={open}
            startsGroup={startsGroup}
            endsGroup={endsGroup}
            separatedFromPrevious={separatedFromPrevious}
            contentId={contentId}
            triggerId={triggerId}
            reduce={reduce}
            classNames={classNames}
            onToggle={() => toggleItem(item.id)}
            onConfigure={() => configureItem(item)}
            onDelete={() => deleteItem(item.id)}
            onRunSimulation={() => runSimulation(item)}
            isRunning={runningSimulationId === item.id}
            simulationResult={simulationResults[item.id]}
          />
        );
      })}

      {configuredItem && (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4"
          role="presentation"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setConfiguredItem(null);
          }}
        >
          <form
            role="dialog"
            aria-modal="true"
            aria-labelledby="configuration-title"
            onSubmit={saveConfiguration}
            className="w-full max-w-md rounded-2xl bg-white p-6 text-slate-900 shadow-2xl dark:bg-neutral-900 dark:text-neutral-100"
          >
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <h2 id="configuration-title" className="text-lg font-semibold">
                  Configure {configuredItem.title}
                </h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Adjust the simulation settings.
                </p>
              </div>
              <button
                type="button"
                aria-label="Close configuration"
                title="Close configuration"
                onClick={() => setConfiguredItem(null)}
                className="grid h-8 w-8 shrink-0 place-items-center rounded-md text-muted-foreground hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
              >
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
            </div>

            <div className="mb-4 grid gap-1.5 text-sm font-medium">
              Simulation name
              <input
                type="text"
                aria-label="Simulation name"
                value={configurationName}
                onChange={(event) => setConfigurationName(event.target.value)}
                required
                className="h-10 rounded-md border border-neutral-700 bg-neutral-800 px-3 font-normal text-neutral-100 outline-none transition-colors hover:bg-neutral-700 focus-visible:ring-2 focus-visible:ring-neutral-400"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {configurationVariables.map((variable) => (
                <label key={variable.name} className="grid gap-1.5 text-sm font-medium">
                  {variable.name}
                  <select
                    aria-label={`${variable.name} label`}
                    value={configuration[variable.name] ?? ""}
                    onChange={(event) =>
                      setConfiguration((current) => ({
                        ...current,
                        [variable.name]: event.target.value,
                      }))
                    }
                    className="h-10 rounded-md border border-neutral-700 bg-neutral-800 px-3 font-normal text-neutral-100 outline-none transition-colors hover:bg-neutral-700 focus-visible:ring-2 focus-visible:ring-neutral-400"
                  >
                    {variable.labels.map((label) => (
                      <option
                        key={label}
                        value={label}
                        className="bg-neutral-800 text-neutral-100 hover:bg-neutral-600"
                      >
                        {label}
                      </option>
                    ))}
                  </select>
                </label>
              ))}
            </div>

            <div className="mt-6 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setConfiguredItem(null)}
                className="rounded-md border-2 border-neutral-300 px-4 py-2 text-sm font-semibold text-neutral-700 shadow-[3px_3px_0_0_#a3a3a3] transition-all hover:translate-x-px hover:translate-y-px hover:bg-neutral-100 hover:shadow-[1px_1px_0_0_#a3a3a3] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-400 active:translate-x-[3px] active:translate-y-[3px] active:shadow-none dark:border-neutral-500 dark:text-neutral-100 dark:shadow-[3px_3px_0_0_#737373] dark:hover:bg-neutral-800"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded-md border-2 border-black bg-black px-4 py-2 text-sm font-semibold text-white shadow-[3px_3px_0_0_#a3a3a3] transition-all hover:translate-x-px hover:translate-y-px hover:bg-neutral-800 hover:shadow-[1px_1px_0_0_#a3a3a3] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-black active:translate-x-[3px] active:translate-y-[3px] active:shadow-none dark:border-white dark:bg-white dark:text-black dark:shadow-[3px_3px_0_0_#737373] dark:hover:bg-neutral-200 dark:focus-visible:outline-white"
              >
                Save configuration
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default function BouncyAccordionPreview({ items = [] }) {
  return <div className="min-h-96 w-full"><BouncyAccordion items={items} /></div>;
}