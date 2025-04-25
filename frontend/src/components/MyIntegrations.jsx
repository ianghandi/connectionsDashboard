import React, { useEffect, useState } from "react";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import { motion } from "framer-motion";

const MyIntegrations = () => {
  const [environment, setEnvironment] = useState("dev");
  const [connectionType, setConnectionType] = useState("saml");
  const [allConnections, setAllConnections] = useState([]);
  const [filteredConnections, setFilteredConnections] = useState([]);
  const [visibleColumns, setVisibleColumns] = useState([]);
  const [columnFilters, setColumnFilters] = useState({});
  const [isDarkMode, setIsDarkMode] = useState(() => localStorage.getItem("theme") === "dark");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode);
    localStorage.setItem("theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  useEffect(() => {
    const fetchConnections = async () => {
      const res = await fetch(`/api/${connectionType}-connections?env=${environment}`);
      const data = await res.json();

      console.log("[DEBUG] Fetched data:", data);

      if (!Array.isArray(data)) {
        console.error("❌ Expected array but got:", data);
        setAllConnections([]);
        setFilteredConnections([]);
        return;
      }

      setAllConnections(data);
      setFilteredConnections(data);
      setVisibleColumns(Object.keys(data[0] || {}));
      setColumnFilters({});
    };

    fetchConnections();
  }, [environment, connectionType]);

  useEffect(() => {
    const filtered = allConnections.filter(conn =>
      Object.entries(columnFilters).every(([key, value]) =>
        value ? String(conn[key] || "").toLowerCase().includes(value.toLowerCase()) : true
      )
    );
    setFilteredConnections(filtered);
  }, [columnFilters, allConnections]);

  const exportToExcel = () => {
    const data = filteredConnections.map(conn => {
      const filtered = {};
      visibleColumns.forEach(col => filtered[col] = conn[col]);
      return filtered;
    });
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Connections");
    const blob = new Blob([XLSX.write(workbook, { bookType: "xlsx", type: "array" })], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    saveAs(blob, `${connectionType}_connections_${environment}.xlsx`);
  };

  const handleColumnToggle = (column) => {
    setVisibleColumns(prev =>
      prev.includes(column) ? prev.filter(col => col !== column) : [...prev, column]
    );
  };

  const handleFilterChange = (column, value) => {
    setColumnFilters(prev => ({ ...prev, [column]: value }));
  };

  return (
    <motion.div
      className="p-6 dark:bg-gray-900 bg-gray-50 rounded-xl shadow-xl min-h-screen text-gray-900 dark:text-gray-100"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex flex-wrap gap-4 items-center mb-6 justify-between">
        <div className="flex gap-4">
          <select
            className="border border-gray-300 dark:border-gray-700 p-2 rounded-md shadow-sm focus:ring-2 focus:ring-blue-400 bg-white dark:bg-gray-800"
            value={environment}
            onChange={(e) => setEnvironment(e.target.value)}
          >
            <option value="dev">Dev</option>
            <option value="qa">QA</option>
            <option value="prod">Prod</option>
          </select>

          <select
            className="border border-gray-300 dark:border-gray-700 p-2 rounded-md shadow-sm focus:ring-2 focus:ring-blue-400 bg-white dark:bg-gray-800"
            value={connectionType}
            onChange={(e) => setConnectionType(e.target.value)}
          >
            <option value="saml">SAML</option>
            <option value="oauth">OAuth</option>
          </select>

          <button
            onClick={exportToExcel}
            className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold px-4 py-2 rounded-md shadow-md transition-all duration-200"
          >
            Export Visible Rows
          </button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Dark Mode</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" className="sr-only peer" checked={isDarkMode} onChange={() => setIsDarkMode(!isDarkMode)} />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-400 dark:bg-gray-700 peer-checked:bg-blue-600 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
          </label>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Select Columns:</h2>
        <div className="flex flex-wrap gap-4">
          {(Object.keys(allConnections[0] || {})).map((col) => (
            <label key={col} className="flex items-center space-x-2">
              <input
                type="checkbox"
                className="accent-blue-600"
                checked={visibleColumns.includes(col)}
                onChange={() => handleColumnToggle(col)}
              />
              <span className="text-sm font-medium">{col}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-lg font-semibold mb-2">Filter Columns:</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {visibleColumns.map((col) => (
            <div key={col} className="flex flex-col">
              <label className="text-sm font-medium mb-1">{col}</label>
              <input
                type="text"
                className="border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-md p-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                placeholder={`Filter ${col}`}
                value={columnFilters[col] || ""}
                onChange={(e) => handleFilterChange(col, e.target.value)}
              />
            </div>
          ))}
        </div>
      </div>

      {filteredConnections.length === 0 ? (
        <div className="text-center py-10 text-gray-500 dark:text-gray-400">
          No connections found or data could not be loaded.
        </div>
      ) : (
        <div className="overflow-auto max-h-[600px] border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm">
          <table className="min-w-full text-sm text-left">
            <thead className="sticky top-0 z-10 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs uppercase">
              <tr>
                {visibleColumns.map((col) => (
                  <th key={col} className="px-4 py-3 border-b border-gray-300 dark:border-gray-600">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredConnections.map((conn, idx) => (
                <motion.tr
                  key={idx}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.01 }}
                  className="hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
                >
                  {visibleColumns.map((col) => (
                    <td key={col} className="px-4 py-2 border-b border-gray-200 dark:border-gray-600">
                      {Array.isArray(conn[col]) ? conn[col].join(", ") : conn[col]}
                    </td>
                  ))}
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
};

export default MyIntegrations;
