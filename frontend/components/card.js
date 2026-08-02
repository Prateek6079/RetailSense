

export default function Card({ content, icon, title, description }) {
  return (
    <div className="group relative block h-64 sm:h-80 lg:h-96">
      <span className="absolute inset-0 border-2 border-dashed border-white"></span>

      <div className="relative h-full overflow-hidden border-2 border-white bg-black transition-transform group-hover:-translate-x-2 group-hover:-translate-y-2">
          <div className="absolute inset-0 px-4 sm:px-6 lg:px-8 transition-opacity duration-300 group-hover:opacity-0">
            <div className="flex mt-7 h-10 w-full">
              {icon}

              <h2 className="ml-5 text-xl font-bold sm:text-2xl">
                {title}
              </h2>
            </div>

            <div className="w-full border-2 border-gray-400 border-dashed h-74 mt-2 pt-2">
              {content}
            </div>
          </div>

        <div className="absolute inset-0 p-4 sm:p-6 lg:p-8 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
          <h3 className="text-xl font-bold sm:text-2xl">
            {title}
          </h3>

          <p className="mt-4 text-sm sm:text-base">
            {description}
          </p>

          <p className="mt-8 font-bold">Read more</p>
        </div>
      </div>
    </div>
  );
}