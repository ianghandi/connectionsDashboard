import React, { useEffect, useState } from "react";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";

const MyIntegrations = () => {
  const [environment, setEnvironment] = useState("dev");
  const [connectionType, setConnectionType] = useState("saml");
  const [allConnections, setAllConnections] = useState([]);
  const [filteredConnections, setFilteredConnections] = useState([]);
  const [visibleColumns, setVisibleColumns] = useState([]);
  const [columnFilters, setColumnFilters] = useState({});

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
      const row = {};
      visibleColumns.forEach(col => {
        row[col] = conn[col];
      });
      return row;
    });
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Connections");
    const blob = new Blob([XLSX.write(workbook, { bookType: "xlsx", type: "array" })], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    saveAs(blob, `${connectionType}_connections_${environment}.xlsx`);
  };

  return (
    <div className="p-6">
      <div className="flex gap-4 mb-4">
        <select value={environment} onChange={(e) => setEnvironment(e.target.value)} className="border p-2 rounded">
          <option value="dev">Dev</option>
          <option value="qa">QA</option>
          <option value="prod">Prod</option>
        </select>
        <select value={connectionType} onChange={(e) => setConnectionType(e.target.value)} className="border p-2 rounded">
          <option value="saml">SAML</option>
          <option value="oauth">OAuth</option>
        </select>
        <button onClick={exportToExcel} className="bg-blue-600 text-white px-4 py-2 rounded">Export</button>
      </div>

      {filteredConnections.length === 0 ? (
        <div className="text-gray-600">No connections to display.</div>
      ) : (
        <div className="overflow-auto max-h-[600px] border rounded">
          <table className="min-w-full border-collapse">
            <thead>
              <tr>
                {visibleColumns.map(col => (
                  <th key={col} className="px-4 py-2 border bg-gray-100">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredConnections.map((conn, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  {visibleColumns.map(col => (
                    <td key={col} className="px-4 py-2 border">{Array.isArray(conn[col]) ? conn[col].join(", ") : conn[col]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default MyIntegrations;
