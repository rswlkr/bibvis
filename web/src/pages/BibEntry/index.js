import React, { useState } from 'react'

const BibEntry = () => {
  const [bibdata, setbibdata] = useState('')
  const submitBibtex = async () => {
    await fetch('localhost:')
    console.log("hello world")
  }
  return (
    <textarea value={bibdata} onChange={(e) => setbibdata(e.target.value)}  onKeyDown={(e) => {
      if((e.shiftKey && e.keyCode === 13)) {
        submitBibtex()
      }
    }} placeholder="paste your bibtext" style={{zIndex:'99999', width:'100%',height:'100%',background:'black', color:'white', position:'absolute','::focus': { 'outline': 'none' }, border:'1px solid black', resize:'none' }}></textarea>
  )
}

export default BibEntry